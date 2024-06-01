from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING
from .setup_cls import TestSetUp
from pytils.translit import slugify


class TestLogic(TestSetUp):

    @classmethod
    def setUpTestData(cls):
        TestSetUp.setUpTestData()
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug',
        }

    def test_create_note(self):
        url = reverse('notes:add')
        Note.objects.all().delete()
        response = self.author_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 1)
        new_note = Note.objects.get()
        assert new_note.title == self.form_data['title']
        assert new_note.text == self.form_data['text']
        assert new_note.slug == self.form_data['slug']
        assert new_note.author == self.author

    def test_anonymus_user(self):
        url = reverse('notes:add')
        Note.objects.all().delete()
        response = self.client.post(url, self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        self.assertRedirects(response, expected_url)
        assert Note.objects.count() == 0

    def test_not_unique_slug(self):
        Note.objects.all().delete()
        self.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=self.author,
        )
        url = reverse('notes:add')
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(url, data=self.form_data)
        self.assertFormError(response, 'form', 'slug', errors=(self.note.slug + WARNING))
        assert Note.objects.count() == 1

    def test_empty_slug(self):
        url = reverse('notes:add')
        Note.objects.all().delete()
        self.form_data.pop('slug')
        response = self.author_client.post(url, data=self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        assert Note.objects.count() == 1
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        assert new_note.slug == expected_slug
     
    def test_author_can_edit(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.author_client.post(url, self.form_data)
        self.assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        assert self.note.title == self.form_data['title']
        assert self.note.text == self.form_data['text']
        assert self.note.slug == self.form_data['slug']

    def test_other_cant_edit(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        response = self.non_author_client.post(url, self.form_data)
        assert response.status_code == HTTPStatus.NOT_FOUND
        self.note_from_db = Note.objects.get(id=self.note.id)
        self.note.refresh_from_db()
        assert self.note.title == self.note_from_db.title
        assert self.note.text == self.note_from_db.text
        assert self.note.slug == self.note_from_db.slug
