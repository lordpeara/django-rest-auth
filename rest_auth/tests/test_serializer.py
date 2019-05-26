# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.test.utils import override_settings

from rest_framework.settings import api_settings

from rest_auth.serializers import UserSerializer


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
