from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from http import HTTPStatus

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='UserName')
        cls.author = User.objects.create_user(username='PostAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_urls_for_unauthorized_users(self):
        """Доступность страниц неавторизованному пользователю."""
        urls_status = {
            '/': HTTPStatus.OK,
            f'/group/{self.group.slug}/': HTTPStatus.OK,
            f'/profile/{self.user.username}/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND
        }
        for address, status_code in urls_status.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, status_code)

    def test_urls_redirect_for_unauthorized_users(self):
        """Страницы /create/ и /posts/<post_id>/edit/ перенаправляют
        неавторизированного пользователя на страницу авторизации.
        """
        urls = (
            f'/posts/{self.post.id}/edit/',
            '/create/'
        )
        for address in urls:
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={address}')

    def test_create_url_exists_at_desired_location_authorized(self):
        """Страница /create/ доступна авторизированному пользователю."""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_exists_for_authors(self):
        """Страница /posts/<post_id>/edit/ доступна автору."""
        response = self.author_client.get(f'/posts/{self.post.id}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_url_redirect_for_not_author(self):
        """Страница по адресу /posts/<post_id>/edit/ перенаправляет не автора
        пользователя на страницу /posts/<post_id>/.
        """
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/edit/',
            follow=True
        )
        self.assertRedirects(response, f'/posts/{self.post.id}/')

    def test_urls_use_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        url_templates_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for address, template in url_templates_names.items():
            with self.subTest(address=address):
                response = self.author_client.get(address)
                self.assertTemplateUsed(response, template)


class CommentURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)

    def test_comment_from_unauthorized(self):
        '''Неавторизованные пользователи при попытке комментирования
        перенаправляются на страницу авторизации.'''
        address = f'/posts/{self.post.id}/comment/'
        response = self.guest_client.get(
            address,
            follow=True
        )
        self.assertRedirects(response, f'/auth/login/?next={address}')

    def test_comment_from_authorized(self):
        """Комментирование доступно авторизованному пользователю."""
        response = self.authorized_client.get(
            f'/posts/{self.post.id}/comment/',
            follow=True
        )
        self.assertRedirects(response, f'/posts/{self.post.id}/')
