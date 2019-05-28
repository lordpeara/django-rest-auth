# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from mock import patch

from django import forms
from django.contrib.auth import get_user_model
from django.core.mail.backends.dummy import EmailBackend
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings

from rest_framework.settings import api_settings

from rest_auth.serializers import (
    LoginSerializer, PasswordChangeSerializer, PasswordResetSerializer,
    UserSerializer,
)

UserModel = get_user_model()


class UserSerializerTest(TestCase):
    PASSWORD_VALIDATORS = [{
        'NAME': (
            'django.contrib.auth.password_validation.MinimumLengthValidator'
        ),
    }]

    def test_create_user(self):
        data = {
            'username': 'test-user',
            'email': 'a@a.com',
            'password1': '23tf123g@f',
            'password2': '23tf123g@f',
        }

        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        user = serializer.save()
        self.assertIsNotNone(user)
        # UserSerializer should not save raw password
        self.assertNotEqual(user.password, data['password1'])

    def test_required_fields(self):
        data = {
            'username': '',
            'email': '',
            'password1': '',
            'password2': '',
        }

        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertItemsEqual(
            serializer.errors.keys(),
            ('username', 'email', 'password1', 'password2')
        )

    @override_settings(AUTH_PASSWORD_VALIDATORS=PASSWORD_VALIDATORS)
    def test_invalid_password(self):
        data = {
            'username': 'test-user',
            'email': 'a@a.com',
            'password1': '23tf',
            'password2': '23tf',
        }

        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('password1', serializer.errors)
        self.assertEqual(
            serializer.errors['password1'][0].code,
            'password_too_short'
        )

    def test_password_mismatch(self):
        data = {
            'username': 'test-user',
            'email': 'a@a.com',
            'password1': '23tf123g@f',
            'password2': '23tf123g@',
        }

        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(api_settings.NON_FIELD_ERRORS_KEY, serializer.errors)
        self.assertEqual(
            serializer.errors[api_settings.NON_FIELD_ERRORS_KEY][0].code,
            'password_mismatch',
        )


class _TestModelBackend(object):
    def authenticate(self, request, **credentials):
        return UserModel.objects.get(username=credentials['username'])


class LoginSerializerTest(TestCase):
    CUSTOM_BACKEND = ('rest_auth.tests.test_serializer._TestModelBackend',)

    def setUp(self):
        self.user = UserModel._default_manager.create_user(
            username='test-user', email='test@test.com',
            password='test-password',
        )

    def test_valid_data(self):
        data = {
            'username': 'test-user',
            'password': 'test-password',
        }

        serializer = LoginSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.get_user().pk, self.user.pk)

    def test_incorrect_password(self):
        data = {
            'username': 'test-user',
            'password': 'bad-password',
        }

        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(api_settings.NON_FIELD_ERRORS_KEY, serializer.errors)
        self.assertEqual(
            serializer.errors[api_settings.NON_FIELD_ERRORS_KEY][0].code,
            'invalid_login',
        )

    @override_settings(AUTHENTICATION_BACKENDS=CUSTOM_BACKEND)
    def test_inactive_user_for_custom_modelbackend(self):
        self.user.is_active = False
        self.user.save()

        data = {
            'username': 'test-user',
            'password': 'test-password',
        }

        serializer = LoginSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(api_settings.NON_FIELD_ERRORS_KEY, serializer.errors)

        self.assertItemsEqual(
            serializer.errors[api_settings.NON_FIELD_ERRORS_KEY],
            (serializer.error_messages['inactive'], )
        )


class _TestEmailBackend(EmailBackend):
    email_buffer = []

    def send_messages(self, messages):
        self.email_buffer.extend(list(messages))
        return super(_TestEmailBackend, self).send_messages(messages)


class PasswordResetSerializerTest(TestCase):
    TEST_EMAIL_BACKEND = 'rest_auth.tests.test_serializer._TestEmailBackend'

    def setUp(self):
        UserModel._default_manager.create_user(
            username='test-user', password='test-password',
            email='test@test.com',
        )

    @override_settings(EMAIL_BACKEND=TEST_EMAIL_BACKEND)
    def test_valid_data(self):
        data = {
            'email': 'test@test.com',
        }

        serializer = PasswordResetSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # serializer.save should send email.
        request = RequestFactory().get('/')
        serializer.save(request=request)
        self.assertEqual(len(_TestEmailBackend.email_buffer), 1)

        # check email message
        msg = _TestEmailBackend.email_buffer.pop()
        self.assertItemsEqual(msg.to, (data['email'],))

    @patch('django.forms.fields.EmailField.clean')
    def test_invalid_email(self, mock):
        data = {
            'email': 'test@test.com',
        }

        mock.side_effect = forms.ValidationError('intended side effect')

        serializer = PasswordResetSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    @override_settings(EMAIL_BACKEND=TEST_EMAIL_BACKEND)
    def test_non_existing_user(self):
        data = {
            'email': 'a@a.com',
        }

        serializer = PasswordResetSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        # Email should not be sent.
        request = RequestFactory().get('/')
        serializer.save(request=request)
        self.assertEqual(len(_TestEmailBackend.email_buffer), 0)

    def test_invalid_data(self):
        serializer = PasswordResetSerializer(data={})
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors['email'][0].code, 'required')


class PasswordChangeSerializerTest(TestCase):
    def setUp(self):
        self.user = UserModel._default_manager.create_user(
            username='test-user', email='root@dev.null',
            password='test-password',
        )

    def test_valid_data(self):
        data = {
            'old_password': 'test-password',
            'new_password1': 'new-password',
            'new_password2': 'new-password',
        }

        serializer = PasswordChangeSerializer(self.user, data=data)
        self.assertTrue(serializer.is_valid())

        serializer.save()
        self.assertTrue(self.user.check_password(data['new_password1']))

    def test_incorrect_old_password(self):
        data = {
            'old_password': 'password',
            'new_password1': 'new-password',
            'new_password2': 'new-password',
        }

        serializer = PasswordChangeSerializer(self.user, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('old_password', serializer.errors)
        self.assertEqual(serializer.errors['old_password'][0].code,
                         'password_incorrect')

    def test_password_mismatch(self):
        data = {
            'old_password': 'test-password',
            'new_password1': 'new-password1',
            'new_password2': 'new-password2',
        }

        serializer = PasswordChangeSerializer(self.user, data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn(api_settings.NON_FIELD_ERRORS_KEY, serializer.errors)
        self.assertEqual(
            serializer.errors[api_settings.NON_FIELD_ERRORS_KEY][0].code,
            'password_mismatch'
        )
