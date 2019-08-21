# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.test.client import RequestFactory
from django.test.utils import override_settings
from django.urls import reverse as r
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_auth.users.serializers import UserSerializer
from rest_auth.users.views import (
    EmailVerificationConfirmView,
    UserEmailVerificationMixin,
)

UserModel = get_user_model()


class LoginViewTest(TestCase):
    def setUp(self):
        self.user = UserModel._default_manager.create_user(
            username='user', password='pass', email='user@localhost',
        )

    def test_login(self):
        data = {
            'username': 'user',
            'password': 'pass',
        }
        response = self.client.post(r('login'), data=data)
        self.assertEqual(response.status_code, 200)
        # response should be empty
        self.assertFalse(bool(response.content))

    @override_settings(REST_AUTH_LOGIN_EMPTY_RESPONSE=False)
    def test_login_returns_data(self):
        data = {
            'username': 'user',
            'password': 'pass',
        }
        response = self.client.post(r('login'), data=data)
        self.assertEqual(response.status_code, 200)

        # response should not contain `password`
        data.pop('password')
        self.assertEqual(response.json(), data)


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = UserModel._default_manager.create_user(
            username='user', password='pass', email='user@localhost',
        )
        self.client.login(username='user', password='pass')

    def test_permission(self):
        # anonymous user cannot access to logout
        self.client.logout()
        response = self.client.post(r('logout'))
        self.assertEqual(response.status_code, 403)

    def test_logout(self):
        response = self.client.post(r('logout'))
        self.assertEqual(response.status_code, 200)


class PasswordForgotViewTest(TestCase):
    def setUp(self):
        self.user = UserModel._default_manager.create_user(
            username='user', password='pass', email='user@localhost',
        )

    def test_forgot(self):
        response = self.client.post(
            r('forgot'), data={'email': self.user.email},
        )

        self.assertEqual(response.status_code, 200)


class PasswordChangeViewTest(TestCase):
    def setUp(self):
        self.user = UserModel._default_manager.create_user(
            username='user', password='pass', email='user@localhost',
        )
        self.client.login(username='user', password='pass')

    def test_permission(self):
        self.client.logout()
        response = self.client.post(r('password_change'))
        self.assertEqual(response.status_code, 403)

    def test_user_bound_serializer(self):
        # undefined method calls should initialize serializer normally.
        response = self.client.get(r('password_change'))
        self.assertEqual(response.status_code, 405)

    def test_password_change(self):
        response = self.client.post(
            r('password_change'), data={
                'old_password': 'pass',
                'new_password1': 'password1!',
                'new_password2': 'password1!',
            },
        )

        self.assertEqual(response.status_code, 200)


class EmailVerificationMixinTest(TestCase):
    def test_create(self):
        serializer = UserSerializer(data={})
        mixin = UserEmailVerificationMixin()
        mixin.request = RequestFactory().get('/')

        # intended AssertError because .save called
        # before calling .is_valid
        with self.assertRaises(AssertionError):
            mixin.perform_create(serializer)


class EmailVerificationViewTest(TestCase):

    @override_settings(REST_AUTH_SIGNUP_REQUIRE_EMAIL_CONFIRMATION=True)
    def test_email_verification_should_activate_user(self):
        data = {
            'username': 'test-user',
            'email': 'a@a.com',
            'password1': '23tf123g@f',
            'password2': '23tf123g@f',
        }

        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid())

        request = RequestFactory().get('/')
        user = serializer.save(email_opts={'request': request})

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        token = default_token_generator.make_token(user)
        self.client.get(
            r('verify_email_confirm',
              kwargs=dict(uidb64=uidb64, token=token)),
            follow=True,
        )
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_non_user(self):
        self.client.get(
            r('verify_email_confirm',
              kwargs=dict(uidb64='abcd', token='efgh-ijkl')),
            follow=True,
        )

    def test_invalid_token(self):
        user = UserModel.objects.create(username='test-user')
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        self.client.get(
            r('verify_email_confirm',
              kwargs=dict(uidb64=uidb64, token='efgh-ijkl')),
            follow=True,
        )

    def test_invalid_session(self):
        user = UserModel.objects.create(username='test-user')
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk)).decode()
        self.client.get(r(
            'verify_email_confirm',
            kwargs=dict(
                uidb64=uidb64,
                token=EmailVerificationConfirmView.INTERNAL_VERIFY_URL_TOKEN
            )
        ))
