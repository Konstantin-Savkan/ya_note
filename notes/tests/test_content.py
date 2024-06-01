from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.forms import NoteForm
from .setup_cls import TestSetUp

User = get_user_model()


class TestContent(TestSetUp):

    def test_note_in_list_for_author(self):
        users_notes = ((self.author, True), (self.not_author, False))
        for user, note_in_list in users_notes:
            with self.subTest(user=user):
                url = reverse('notes:list')
                self.client.force_login(user)
                response = self.client.get(url)
                object_list = response.context['object_list']
                assert (self.note in object_list) is note_in_list

    def test_content_form(self):
        name_args = (
            ('notes:add', None),
            ('notes:edit', self.slug_for_args),
        )
        for name, args in name_args:
            with self.subTest(name=name, args=args):
                url = reverse(name, args=args)
                response = self.author_client.get(url)
                assert 'form' in response.context
                assert isinstance(response.context['form'], NoteForm)

