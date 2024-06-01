from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.urls import reverse

from .setup_cls import TestSetUp

User = get_user_model()


class TestRoutes(TestSetUp):

    def test_pages_availability_for_all(self):
        urls = (
            'notes:home',
            'users:login',
            'users:logout',
            'users:signup',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK) 
    
    def test_pages_for_auth_user(self):
        urls = (
            'notes:list',
            'notes:add',
            'notes:success',
        )
        for name in urls:
            with self.subTest(name=name):
                url = reverse(name)
                response = self.non_author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_for_differenf_user(self):
        client_status = (
            (
                self.not_author,
                HTTPStatus.NOT_FOUND,
            ),
            (
                self.author,
                HTTPStatus.OK,
            )
        )
        for user, status in client_status:
            self.client.force_login(user)
            urls = (
                'notes:detail',
                'notes:edit',
                'notes:delete',
            )
            for name in urls:
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertAlmostEqual(response.status_code, status)

    def test_redirect(self):
        login_url = reverse('users:login')
        urls_note = (
            ('notes:detail', self.slug_for_args),
            ('notes:edit', self.slug_for_args),
            ('notes:delete', self.slug_for_args),
            ('notes:add', None),
            ('notes:success', None),
            ('notes:list', None),
        )
        for name, args in urls_note:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                excepted_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, excepted_url)


