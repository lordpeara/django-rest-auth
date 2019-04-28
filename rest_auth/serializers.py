from django.conf import settings
from django.contrib import auth
from django.contrib.auth import get_user_model, password_validation
from django.utils.translation import ugettext_lazy as _

from rest_framework import serializers

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(
        label=_('Password'),
        validators=[password_validation.validate_password],
        help_text=password_validation.password_validators_help_text_html,
        write_only=True,
        style={'input_type': 'password'},
    )
    password2 = serializers.CharField(
        label=_('Password Confirmation'),
        help_text=_("Enter the same password as before, for verification."),
        write_only=True,
        style={'input_type': 'password'},
    )

    default_error_messages = {
        'password_mismatch': _('2 passwords should be equal'),
    }

    class Meta:
        model = UserModel
        fields = (
            UserModel.USERNAME_FIELD, UserModel.EMAIL_FIELD,
            'password1', 'password2',
        )

    def validate(self, data):
        password1 = data.get('password1')
        password2 = data.get('password2')

        data['password2'] =\
            self._validate_password2(password1, password2)

        return data

    def _validate_password2(self, password1, password2):
        if password1 != password2:
            raise serializers.ValidationError(
                self.error_messages['password_mismatch'],
                code='password_mismatch',
            )

        return password2

    def create(self, validated_data):
        user = UserModel._default_manager.create_user(
            validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password1'],
            is_active=True,
        )

        # TODO: user activation through email confirmation.
        require_email_confirmation = getattr(
            settings, 'SIGNUP_REQUIRE_EMAIL_CONFIRMATION', False
        )

        if require_email_confirmation:
            user.is_active = False

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
            "Please enter a correct %(username)s and password. "
            "Note that both fields may be case-sensitive."
        ),
        'inactive': _('This account is inactive.'),
    }

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user = None

        super(LoginSerializer, self).__init__(self, request, *args, **kwargs)

    def validate(self, data):
        username = data['username']
        password = data['password']

        self.user = auth.authenticate(username, password)
        if self.user is None:
            raise serializers.ValidationError(
                self.error_messages['invalid_login'],
                code='invalid_login'
            )

        self._confirm_login_allowed(self.user)

        return data

    def _confirm_login_allowed(self, user):
        if not user.is_active:
            raise serializers.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user(self):
        return self.user
