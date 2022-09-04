from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus
from django import utils
from django.contrib.auth.tokens import default_token_generator

User = get_user_model()


class UsersURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_for_unauthorized_users(self):
        """Доступность страниц неавторизованному пользователю."""
        uidb64 = utils.http.urlsafe_base64_encode(
            utils.encoding.force_bytes(1)
        )
        token = default_token_generator.make_token(self.user)
        urls_status = {
            '/auth/signup/': HTTPStatus.OK,
            '/auth/logout/': HTTPStatus.OK,
            '/auth/login/': HTTPStatus.OK,
            '/auth/password_reset/': HTTPStatus.OK,
            '/auth/password_reset/done/': HTTPStatus.OK,
            '/auth/reset/done/': HTTPStatus.OK,
            f'/auth/reset/{uidb64}/{token}/': HTTPStatus.OK
        }
        for address, status_code in urls_status.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertEqual(response.status_code, status_code)

    def test_urls_redirect_for_unauthorized_users(self):
        """Страницы /password_change/ и /password_change/done/ перенаправляют
        неавторизированного пользователя на страницу авторизации.
        """
        urls = (
            '/auth/password_change/',
            '/auth/password_change/done/'
        )
        for address in urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={address}')

    def test_urls_exist_at_desired_location_authorized(self):
        """Страницы /password_change/ и /password_change/done/ доступны
        для авторизованного пользователя.
        """
        urls_status = {
            '/auth/password_change/': HTTPStatus.OK,
            '/auth/password_change/done/': HTTPStatus.OK
        }
        for address, status_code in urls_status.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertEqual(response.status_code, status_code)

    def test_urls_use_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        uidb64 = utils.http.urlsafe_base64_encode(
            utils.encoding.force_bytes(1)
        )
        token = default_token_generator.make_token(self.user)
        url_templates_names = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset_form.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/password_change/': 'users/password_change_form.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
            f'/auth/reset/{uidb64}/{token}/':
            'users/password_reset_confirm.html',
            '/auth/logout/': 'users/logged_out.html'
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertTemplateUsed(response, template)
