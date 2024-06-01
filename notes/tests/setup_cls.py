from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from notes.models import Note

User = get_user_model()


class TestSetUp(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Лев Толстой')
        cls.not_author = User.objects.create(username='Читатель простой')
        cls.author_client = Client()
        cls.non_author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.non_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author
        )
        cls.slug_for_args = (cls.note.slug,)
