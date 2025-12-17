from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from pallets.models import Palet


class PaletAdminTest(TestCase):
    def setUp(self):
        """Подготовка данных для тестов админ-панели."""
        self.client = Client()
        # Создаем суперпользователя для доступа к админке
        self.superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="password123"
        )
        self.client.login(username="admin", password="password123")

        # Создаем тестовые данные
        self.palet1 = Palet.objects.create(
            number=201,
            pallets_from_the_date=timezone.now().date(),
            receipt_mark=False,
        )
        self.palet2 = Palet.objects.create(
            number=202,
            pallets_from_the_date=timezone.now().date(),
            receipt_mark=False,
        )

    def test_print_selected_palets_action(self):
        """Проверяет кастомное действие 'Печать выбранных паллет' в админке."""
        # URL для страницы списка паллет в админке
        url = reverse("admin:pallets_palet_changelist")

        # Данные, которые отправляются при выполнении действия
        post_data = {
            "action": "print_selected_palets",
            "_selected_action": [self.palet1.id, self.palet2.id],
        }

        response = self.client.post(url, post_data)

        # Проверяем, что действие вернуло PDF-файл
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF-"))
        self.assertIn('filename="selected_palets.pdf"', response["Content-Disposition"])
