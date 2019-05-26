# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        label=_('Password'),
        validators=[password_validation.validate_password],
        help_text=password_validation.password_validators_help_text_html(),
        write_only=True,
        style={'input_type': 'password'},
    )
    password2 = serializers.CharField(
        label=_('Password Confirmation'),
        help_text=_('Enter the same password as before, for verification.'),
        write_only=True,
        style={'input_type': 'password'},
    )

    default_error_messages = {
        'password_mismatch': _('2 passwords should be equal'),
    }

    class Meta:
        model = UserModel
        fields = (
            UserModel.USERNAME_FIELD, UserModel.get_email_field_name(),
            'password1', 'password2',
        )

        extra_kwargs = {
            UserModel.get_email_field_name(): {
                'required': True,
                'allow_blank': False,
            },
        }

    def validate(self, data):
        password1 = data.get('password1')
        password2 = data.get('password2')

        data['password2'] = self._validate_password2(password1, password2)

        return data

    def _validate_password2(self, password1, password2):
        if password1 != password2:
            raise serializers.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        return password2

    def save(self, **kwargs):
        password = self.validated_data.pop('password1')
        self.validated_data.pop('password2')

        # NOTE Because ModelSerializer.save calls model._default_manager.save()
        # , we should set user's password manually.
        user = super(UserSerializer, self).save(**kwargs)
        user.set_password(password)

        # TODO: user activation through email confirmation.
        require_email_confirmation = getattr(
            settings, 'REST_AUTH_SIGNUP_REQUIRE_EMAIL_CONFIRMATION', False
        )

        if require_email_confirmation:
            user.is_active = False

        user.save()

        return user


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(
        label=_('Username'), max_length=254,
    )

    password = serializers.CharField(
        label=_('Password'),
        style={'input_type': 'password'},
    )

    default_error_messages = {
        'invalid_login': _(
            'Please enter a correct username and password. '
            'Note that both fields may be case-sensitive.'
        ),
        'inactive': _('This account is inactive.'),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None

        super(LoginSerializer, self).__init__(request, *args, **kwargs)

    def validate(self, data):
        username = data['username']
        password = data['password']

        self.user = auth.authenticate(username=username, password=password)
        if self.user is None:
            raise serializers.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login',
            )

        self.confirm_login_allowed(self.user)

        return data

    def confirm_login_allowed(self, user):
        """Override this method if you use custom authentication method
        and have additional methods for allowing logins.
        """

        # XXX NOTE This condition doesn't have any effects
        # if you use `django.contrib.auth.backends.ModelBackend`
        # It's useful just for custom backends
        if not user.is_active:
            raise serializers.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user(self):
        return self.user


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField(
        label=_('Email'), max_length=254,
    )

    password_reset_form_class = PasswordResetForm

    def validate_email(self, value):
        self.form = self.password_reset_form_class(data=self.initial_data)
        if not self.form.is_valid():
            if 'email' in self.form.errors:
                raise serializers.ValidationError(self.form.errors['email'])
            # XXX non email errors should be catched & re-raised
            # (if django's PasswordResetForm add new fields)

        return value

    def save(self, domain_override=None,
             subject_template_name='registration/password_reset_subject.txt',
             email_template_name='registration/password_reset_email.html',
             use_https=True, token_generator=default_token_generator,
             from_email=None, request=None, html_email_template_name=None,
             extra_email_context=None):

        return self.form.save(
            domain_override=domain_override,
            subject_template_name=subject_template_name,
            email_template_name=email_template_name, use_https=use_https,
            token_generator=token_generator, from_email=from_email,
            request=request, html_email_template_name=html_email_template_name,
            extra_email_context=extra_email_context,
        )


class SetPasswordSerializer(serializers.Serializer):
    new_password1 = serializers.CharField(
        label=_('New password'),
        validators=[password_validation.validate_password],
        help_text=password_validation.password_validators_help_text_html(),
        write_only=True,
        style={'input_type': 'password'},
    )

    new_password2 = serializers.CharField(
        label=_('New password confirmation'),
        help_text=_('Enter the same password as before, for verification.'),
        write_only=True,
        style={'input_type': 'password'},
    )

    default_error_messages = {
        'password_mismatch': _('2 passwords should be equal'),
    }

    def __init__(self, user=None, *args, **kwargs):
        self.user = user
        super(SetPasswordSerializer, self).__init__(*args, **kwargs)

    def validate(self, data):
        password1 = data.get('new_password1')
        password2 = data.get('new_password2')

        data['new_password2'] =\
            self._validate_new_password2(password1, password2)

        return data

    def _validate_new_password2(self, password1, password2):
        if password1 != password2:
            raise serializers.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        return password2

    def save(self, commit=True):
        password = self.validated_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()

        return self.user


class PasswordChangeSerializer(SetPasswordSerializer):
    old_password = serializers.CharField(
        label=_('Old password'),
        write_only=True,
        style={'input_type': 'password'},
    )

    default_error_messages = {
        'password_incorrect': _('Your old password was entered incorrectly. '
                                'Please enter it again.'),
    }

    def validate_old_password(self, old_password):
        if not self.user.check_password(old_password):
            raise serializers.ValidationError(
                self.error_messages['password_incorrect'],
                code='password_incorrect'
            )

        return old_password
