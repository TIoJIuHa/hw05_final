from django.test import TestCase, Client
from http import HTTPStatus
from django.urls import reverse


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_exists_at_desired_location(self):
        """Проверка доступности статичных страниц."""
        urls_status = {
            '/about/author/': HTTPStatus.OK,
            '/about/tech/': HTTPStatus.OK
        }
        for address, status_code in urls_status.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_urls_use_correct_template(self):
        """Проверка шаблонов для статичных страниц."""
        url_templates_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html'
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)


class StaticPagesViewsTests(TestCase):
    """URL-адрес использует соответствующий шаблон."""
    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        url_templates_names = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html'
        }
        for reverse_name, template in url_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
