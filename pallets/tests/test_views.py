from unittest.mock import patch

from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from pallets.models import Palet, Poducts_in_palet, Poducts_in_palet_quantity


class PaletViewsTest(TestCase):
    def setUp(self):
        """Подготовка данных для тестов представлений."""
        self.client = Client()
        self.palet = Palet.objects.create(
            number=102,
            pallets_from_the_date=timezone.now().date(),
            receipt_mark=False,
        )
        self.product = Poducts_in_palet.objects.create(product_name="Тестовый продукт для view")
        Poducts_in_palet_quantity.objects.create(
            palet=self.palet, product=self.product, quantity=20
        )

    def test_palet_list_view(self):
        """Проверяет, что представление palet_list доступно и отображает паллеты."""
        url = reverse("pallets:palet_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "102")  # Проверяем наличие номера паллеты
        self.assertTemplateUsed(response, "pallets/palet_list.html")

    @patch("pallets.views.requests.request")
    def test_send_palet_success(self, mock_request):
        """Проверяет успешную отправку паллеты в Yougile."""
        # Мокируем успешный ответ от API
        mock_request.return_value.raise_for_status.return_value = None

        url = reverse("pallets:send_palet", args=[self.palet.id])
        response = self.client.post(url)

        # Проверяем редирект
        self.assertRedirects(response, reverse("pallets:palet_list"))

        # Проверяем, что паллета помечена как заказанная
        self.palet.refresh_from_db()
        self.assertTrue(self.palet.receipt_mark)

        # Проверяем, что API был вызван
        mock_request.assert_called_once()

    @patch("pallets.views.requests.request")
    def test_send_palet_failure(self, mock_request):
        """Проверяет обработку ошибки при отправке паллеты в Yougile."""
        # Мокируем ошибку от API
        mock_request.return_value.raise_for_status.side_effect = Exception("API Error")

        url = reverse("pallets:send_palet", args=[self.palet.id])
        response = self.client.post(url)

        # Проверяем редирект
        self.assertRedirects(response, reverse("pallets:palet_list"))

        # Проверяем, что статус паллеты НЕ изменился
        self.palet.refresh_from_db()
        self.assertFalse(self.palet.receipt_mark)

        # Проверяем, что API был вызван
        mock_request.assert_called_once()

    def test_print_palets_pdf_view(self):
        """Проверяет генерацию PDF для выбранных паллет."""
        # Создадим еще одну паллету для теста
        palet2 = Palet.objects.create(
            number=103,
            pallets_from_the_date=timezone.now().date(),
            receipt_mark=False,
        )

        url = reverse("pallets:print_palets_pdf")

        # Данные, которые мы отправляем в POST-запросе
        post_data = {"palet_ids": [self.palet.id, palet2.id]}

        response = self.client.post(url, post_data)

        # 1. Проверяем, что ответ успешный
        self.assertEqual(response.status_code, 200)

        # 2. Проверяем тип контента
        self.assertEqual(response["Content-Type"], "application/pdf")

        # 3. Проверяем заголовок, который предлагает скачать файл
        self.assertEqual(response["Content-Disposition"], 'attachment; filename="pallets.pdf"')

        # 4. Проверяем, что тело ответа начинается с магических байт PDF (%PDF-)
        # Это простой, но эффективный способ убедиться, что сгенерирован именно PDF-файл.
        self.assertTrue(response.content.startswith(b"%PDF-"))
