from django.test import TestCase
from django.utils import timezone

from pallets.models import Palet, Poducts_in_palet, Poducts_in_palet_quantity


class PaletModelTest(TestCase):
    def setUp(self):
        """Подготовка данных для тестов моделей."""
        self.product = Poducts_in_palet.objects.create(product_name="Тестовый продукт")
        self.palet = Palet.objects.create(
            number=101,
            pallets_from_the_date=timezone.now().date(),
            receipt_mark=False,
        )
        self.quantity = Poducts_in_palet_quantity.objects.create(
            palet=self.palet, product=self.product, quantity=10
        )

    def test_model_str_representation(self):
        """Проверяет строковое представление моделей."""
        self.assertEqual(str(self.product), "Тестовый продукт")
        self.assertEqual(str(self.palet), "101")
        self.assertEqual(str(self.quantity), "Тестовый продукт - 10 шт.")

    def test_get_products_list(self):
        """Проверяет метод get_products_list в модели Palet."""
        # Добавим еще один продукт для проверки
        product2 = Poducts_in_palet.objects.create(product_name="Продукт 2")
        Poducts_in_palet_quantity.objects.create(palet=self.palet, product=product2, quantity=5)

        expected_html = "Тестовый продукт - 10 шт.<br>Продукт 2 - 5 шт."
        self.assertEqual(self.palet.get_products_list(), expected_html)
