# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse as r

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


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = UserModel._default_manager.create_user(
            username='user', password='pass', email='user@localhost',
        )
        self.client.login(username='user', password='pass')

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
