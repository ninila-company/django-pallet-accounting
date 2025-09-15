from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField
from django.db import models
from django.utils.html import format_html


class Poducts_in_palet(models.Model):
    product_name = models.CharField(max_length=255, verbose_name="Товар")
    # Поле для полнотекстового поиска. null=True, чтобы можно было добавить в существующую таблицу.
    search_vector = SearchVectorField(null=True, editable=False)

    def __str__(self):
        return self.product_name

    class Meta:
        verbose_name = "Продукт в палете"
        verbose_name_plural = "Продукты в палете"
        # Добавляем GiN-индекс для поля search_vector
        indexes = [
            GinIndex(fields=["search_vector"]),
        ]


class Palet(models.Model):
    number = models.IntegerField(verbose_name="Номер палеты")
    pallets_from_the_date = models.DateField(verbose_name="Дата поступления")
    pallet_pick_up_date = models.DateField(blank=True, null=True, verbose_name="Дата получения")
    receipt_mark = models.BooleanField(default=False, verbose_name="Отметка о заказе")

    def __str__(self):
        return str(self.number)

    class Meta:
        verbose_name = "Палета"
        verbose_name_plural = "Палеты"

    def get_products_list(self):
        products = []
        for product_quantity in self.products_quantity.all():
            products.append(
                f"{product_quantity.product.product_name} - {product_quantity.quantity} шт."
            )
        return format_html("<br>".join(products))

    get_products_list.short_description = "Продукты"


class Poducts_in_palet_quantity(models.Model):
    palet = models.ForeignKey(
        Palet,
        on_delete=models.CASCADE,
        related_name="products_quantity",
        verbose_name="Палета",
    )
    product = models.ForeignKey(Poducts_in_palet, on_delete=models.CASCADE, verbose_name="Продукт")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")

    def __str__(self):
        return f"{self.product.product_name} - {self.quantity} шт."
    class Meta:
        verbose_name = "Продукт в палете с количеством"
        verbose_name_plural = "Продукты в палете с количеством"
