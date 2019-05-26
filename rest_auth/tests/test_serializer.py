# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.utils import override_settings

from rest_framework.settings import api_settings

from rest_auth.serializers import (
    LoginSerializer, UserSerializer,
)


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
    UserModel = get_user_model()

    def authenticate(self, request, **credentials):
        try:
            user = self.UserModel.objects.get(username=credentials['username'])
        except self.UserModel.DoesNotExist:
            user = None

        return user


class LoginSerializerTest(TestCase):
    UserModel = get_user_model()

    def setUp(self):
        self.user = self.UserModel._default_manager.create_user(
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

    @override_settings(
        AUTHENTICATION_BACKENDS=(
            'rest_auth.tests.test_serializer._TestModelBackend',
        )
    )
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
