import shutil
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings
from django.core.cache import cache
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms

from posts.models import Group, Post, Comment, Follow

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='FirstAuthor')
        cls.group = Group.objects.create(
            title='Тестовая первая группа',
            slug='test_slug_1',
            description='Тестовое первое описание',
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='Тестовый первый пост',
            group=cls.group
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def check_post(self, response):
        post_obj = response.context.get('page_obj')[0]
        self.assertEqual(post_obj.text, self.post.text)
        self.assertEqual(post_obj.author.username, self.author.username)
        self.assertEqual(post_obj.group.title, self.group.title)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}): (
                    'posts/group_list.html'),
            reverse(
                'posts:profile',
                kwargs={'username': self.author.username}): (
                    'posts/profile.html'),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): (
                    'posts/post_detail.html'),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): (
                    'posts/create_post.html'),
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for reverse_name, template in pages_templates_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_use_correct_context(self):
        """Шаблон для posts:index сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:index'))
        self.check_post(response)

    def test_group_list_use_correct_context(self):
        """Шаблон для posts:group_list сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        group_obj = response.context['group']
        self.assertEqual(group_obj.title, self.group.title)
        self.assertEqual(group_obj.slug, self.group.slug)
        self.check_post(response)

    def test_post_not_in_another_group(self):
        """Пост не попал в другую группу"""
        another_post = Post.objects.create(
            author=User.objects.create_user(username='SecondAuthor'),
            text='Тестовый второй пост',
            group=Group.objects.create(
                title='Тестовая вторая группа',
                slug='test_slug_2',
                description='Тестовое второе описание',
            )
        )
        response = self.author_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        post = response.context['page_obj'][0]
        self.assertNotIn(another_post.text, post.text)

    def test_post_create_use_correct_context(self):
        """Шаблон для posts:post_create сформирован с правильным контекстом."""
        response = self.author_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_post_edit_use_correct_context(self):
        """Шаблон для posts:post_edit сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_profile_use_correct_context(self):
        """Шаблон для posts:profile сформирован с правильным контекстом"""
        response = self.author_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.author.username}
            )
        )
        self.check_post(response)
        self.assertEqual(
            response.context['author'].username,
            self.author.username
        )

    def test_image_in_post_passed_into_context(self):
        """Проверяем, что картинка поста передаётся в контекст"""
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        post_with_image = Post.objects.create(
            author=self.author,
            text='Тестовый новый пост',
            group=self.group,
            image=uploaded
        )
        urls = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': post_with_image.group.slug}),
            reverse(
                'posts:profile',
                kwargs={'username': post_with_image.author.username}),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': post_with_image.id}),
        )
        for reverse_name in urls:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                if 'page_obj' in response.context:
                    post_obj = response.context.get('page_obj')[0]
                else:
                    post_obj = response.context['post']
                self.assertEqual(post_obj.image, post_with_image.image)

    def test_cache(self):
        '''Проверка кэширования главной страницы.'''
        post = Post.objects.create(
            author=self.author,
            text='Тестовый пост для проверки кэша',
            group=self.group,
        )
        response_before_del = self.author_client.get(reverse('posts:index'))
        post.delete()
        response_after_del = self.author_client.get(reverse('posts:index'))
        self.assertEqual(
            response_before_del.content,
            response_after_del.content
        )
        cache.clear()
        response_after_clear_cache = self.author_client.get(
            reverse('posts:index')
        )
        self.assertNotEqual(
            response_before_del.content,
            response_after_clear_cache.content
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='PostAuthor')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.posts = [Post(
            author=cls.author,
            text='Тестовый пост',
            group=cls.group,
        ) for i in range(settings.POSTS_PER_PAGE + 3)]
        Post.objects.bulk_create(cls.posts)
        cls.names = (
            reverse('posts:index'),
            reverse('posts:group_list',
                    kwargs={'slug': cls.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': cls.author.username})
        )

    def setUp(self):
        cache.clear()
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def test_first_page_contains_ten_records(self):
        "На первой странице отображается 10 постов."
        for reverse_name in self.names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    settings.POSTS_PER_PAGE
                )

    def test_second_page_contains_three_records(self):
        "На второй странице отображается 3 поста."
        for reverse_name in self.names:
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


class CommentTests(TestCase):
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
            text='Тестовый пост',
            group=cls.group,
            author=cls.author,
        )

    def setUp(self):
        self.user = User.objects.create_user(username='TestUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_from_authorized(self):
        '''Комментарий появляется на странице поста'''
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий',
        }
        response = self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True,
        )
        comment = Comment.objects.first()
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
        )
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
            ).exists()
        )
        self.assertEqual(comment.author, self.user)


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='Following')
        cls.follower = User.objects.create_user(username='Follower')
        cls.non_follower = User.objects.create_user(username='NonFollower')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.author,
        )

    def setUp(self):
        self.non_follower_client = Client()
        self.non_follower_client.force_login(self.non_follower)
        self.follower_client = Client()
        self.follower_client.force_login(self.follower)
        self.following_client = Client()
        self.following_client.force_login(self.author)

    def test_follow_and_unfollow(self):
        '''Авторизованный пользователь может подписываться на автора
        и отписываться от него.'''
        follow_count = Follow.objects.count()
        self.follower_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count + 1)
        self.follower_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), follow_count)

    def test_following_pub(self):
        '''Запись автора появляется у тех, кто на него подписан,
        и не появляется у остальных.'''
        self.follower_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username}
            )
        )
        non_follower_response = self.non_follower_client.get(
            reverse('posts:follow_index')
        )
        follower_response = self.follower_client.get(
            reverse('posts:follow_index')
        )
        self.assertNotEqual(
            non_follower_response.content,
            follower_response.content
        )
