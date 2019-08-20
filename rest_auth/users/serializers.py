# -*- coding: utf-8 -*-
from django.conf import settings
from django.contrib.auth import get_user_model, password_validation
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import EmailMultiAlternatives
from django.template import loader
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import ugettext_lazy as _
from rest_framework import serializers

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """User serializer for rest_framework & AUTH_USER_MODEL.

    Fields & methods are built on a django's defualt ``User`` model.
    Extend this serializer if you need your custom user model.

    (Even if ``AUTH_USER_MODEL`` is can be customized, this is recommended
    that You don't change & use customized user model.
    using custom user model is very complex.)

    :param username: ``USERNAME_FIELD`` of ``AUTH_USER_MODEL``
    :param email: ``User.get_email_field_name()``
    :param password1: password of a user (write_only, used only when created)
    :param password2: password confirmation (write_only)

    :TODO: Serializer Only implements creating. list/get are need to be implmtd
    """
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

    EMAIL_FIELD_NAME = UserModel.get_email_field_name()

    def __init__(self, *args, **kwargs):
        super(UserSerializer, self).__init__(*args, **kwargs)

        email_confirm = settings.REST_AUTH_SIGNUP_REQUIRE_EMAIL_CONFIRMATION
        if email_confirm and not hasattr(self, 'EMAIL_FIELD_NAME'):
            raise ImproperlyConfigured(_(
                '%s.EMAIL_FIELD_NAME is required if you want to '
                'enable email verification on sign-up.' % (
                    self.__class__.__name__,
                )
            ))

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
        """Vaildates if two passwords are equal.

        :exception ValidationError: when 2 passwds are different
        """
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

    def create(self, validated_data):
        """Creates user instance

        CAVEAT:

        A clear difference between django's ``ModelForm`` and rest_framework's
        ``ModelSerializer`` is that, model serializer's ``save`` method doesn't
        respect form's ``commit=True``.

        Inside ``super().create``, a query is fired to create user,
        and inside this, additional query is fired to save hashed password.
        It's because ``ModelSerializer``'s ``create`` method uses
        default manager's create function, ``Model._default_manager.create()``

        (User model creation is recommended by calling ``UserManager``'s
        ``create_user`` method)

        :param validated_data: validated data created after ``self.vaildate``
        """
        password = validated_data.pop('password1')
        email_opts = validated_data.pop('email_opts', {})
        validated_data.pop('password2')

        # NOTE We should set user's password manually because
        # ModelSerializer.create calls model._default_manager.save().
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(password)

        # TODO: user activation through email confirmation.
        require_email_confirmation =\
            settings.REST_AUTH_SIGNUP_REQUIRE_EMAIL_CONFIRMATION

        if require_email_confirmation:
            user.is_active = False
            self.send_mail(user, **email_opts)

        user.save()

        return user

    def send_mail(self, user, domain_override=None,
                  subject_template_name='registration/verify_email.txt',
                  email_template_name='registration/verify_email.html',
                  use_https=False, token_generator=default_token_generator,
                  from_email=None, request=None, html_email_template_name=None,
                  extra_email_context=None):
        """Send verification mail to newbie.
        """
        email = self.validated_data[self.EMAIL_FIELD_NAME]

        if domain_override:
            site_name = domain = domain_override
        else:
            current_site = get_current_site(request)
            site_name = current_site.name
            domain = current_site.domain

        protocol = 'https' if use_https else 'http'
        context = {
            'email': email, 'domain': domain, 'site_name': site_name,
            'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
            'user': user,
            'token': token_generator.make_token(user), 'protocol': protocol,
        }
        if extra_email_context is not None:
            context.update(extra_email_context)

        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(
            subject, body, from_email, [email]
        )
        if html_email_template_name is not None:
            html_email = loader.render_to_string(
                html_email_template_name, context
            )
            email_message.attach_alternative(html_email, 'text/html')

        email_message.send()
