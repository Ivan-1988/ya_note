from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from notes.models import Note


User = get_user_model()


class TestNotesList(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Создаем двух пользователей
        cls.user1 = User.objects.create(username='testUser1')
        cls.user2 = User.objects.create(username='testUser2')

        # Создаем заметки для каждого пользователя
        cls.note_user1 = Note.objects.create(
            title='Заметка user1',
            text='Текст заметки',
            author=cls.user1
        )
        cls.note_user2 = Note.objects.create(
            title='Заметка user2',
            text='Текст заметки',
            author=cls.user2
        )

    def test_user_sees_only_own_notes(self):
        self.client.force_login(self.user1)
        url = reverse('notes:list')
        response = self.client.get(url)

        # Проверяем, что ответ успешный
        self.assertEqual(response.status_code, HTTPStatus.OK)

        # Проверяем, что в контексте ответа только заметки user1
        notes_in_context = response.context['object_list']
        self.assertEqual(len(notes_in_context), 1)
        self.assertIn(self.note_user1, notes_in_context)
        self.assertNotIn(self.note_user2, notes_in_context)

    def test_user_cant_see_other_users_notes(self):
        self.client.force_login(self.user1)
        url = reverse('notes:detail', args=(self.note_user2.slug,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
