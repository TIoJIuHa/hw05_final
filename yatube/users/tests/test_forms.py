from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

User = get_user_model()


class UserCreationFormTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_signup(self):
        users_count = User.objects.count()
        form_data = {
            'username': 'pbdujw',
            'password1': 'bkI83bdn8F',
            'password2': 'bkI83bdn8F'
        }
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(
            User.objects.filter(
                username='pbdujw'
            ).exists()
        )
