from django.contrib import admin
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from .models import Palet, Poducts_in_palet, Poducts_in_palet_quantity


class Poducts_in_palet_quantityInline(admin.TabularInline):
    model = Poducts_in_palet_quantity
    extra = 1


@admin.register(Palet)
class PaletAdmin(admin.ModelAdmin):
    list_display = (
        "number",
        "pallets_from_the_date",
        "pallet_pick_up_date",
        "receipt_mark",
        "get_products_list",
    )
    list_filter = ("pallets_from_the_date", "pallet_pick_up_date", "receipt_mark")
    search_fields = ("number", "products_quantity__product__product_name")
    inlines = [Poducts_in_palet_quantityInline]
    # actions = ["print_selected_palets"]

    def get_products_list(self, obj):
        products = []
        for product_quantity in obj.products_quantity.all():
            products.append(
                f"{product_quantity.product.product_name} - {product_quantity.quantity} шт."
            )
        return " /// ".join(products)

    get_products_list.short_description = "Продукты"

    def print_selected_palets(self, request, queryset):
        try:
            palets = queryset
            html_string = render_to_string(
                "palets/print_selected_palets.html", {"palets": palets}
            )
            pdf_file = HTML(string=html_string).write_pdf()

            response = HttpResponse(pdf_file, content_type="application/pdf")
            response["Content-Disposition"] = (
                'attachment; filename="selected_palets.pdf"'
            )
            return response
        except Exception as e:
            self.message_user(
                request, f"Ошибка при генерации PDF: {str(e)}", level="error"
            )
            return

    print_selected_palets.short_description = "Печать выбранных палет"


@admin.register(Poducts_in_palet)
class Poducts_in_paletAdmin(admin.ModelAdmin):
    list_display = ("product_name",)


@admin.register(Poducts_in_palet_quantity)
class Poducts_in_palet_quantityAdmin(admin.ModelAdmin):
    list_display = ("palet", "product", "quantity")
    list_filter = ("palet", "product")
    search_fields = ("palet__number", "product__product_name")
