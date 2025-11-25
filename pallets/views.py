import os
import time

import requests
from django.contrib import messages, postgres

# from django.db.models import Q
from django.db.models import Prefetch
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone

from .models import Palet, Poducts_in_palet_quantity


def palet_list(request):
    search_query = request.GET.get("search", "").strip()

    # Начинаем с базового запроса
    palets_qs = Palet.objects.filter(receipt_mark=False)

    # Определяем базовый prefetch для продуктов
    prefetch_products = Prefetch(
        "products_quantity",
        queryset=Poducts_in_palet_quantity.objects.select_related("product"),
    )

    if search_query:
        # Используем полнотекстовый поиск.
        # search_type='phrase' ищет точную фразу, решая проблему "белый" vs "супербелый".
        # config='russian' указывает, что мы ищем на русском языке.
        query = postgres.search.SearchQuery(search_query, search_type="phrase", config="russian")

        # Фильтруем палеты, как и раньше
        palets_qs = palets_qs.filter(products_quantity__product__search_vector=query)

        # Создаем аннотацию для подсветки
        headline = postgres.search.SearchHeadline(
            "product__product_name",  # Поле, которое нужно подсветить
            query,
            start_sel="<mark>",  # Начальный тег для подсветки
            stop_sel="</mark>",  # Конечный тег
        )

        # Создаем кастомный Prefetch, который добавляет аннотацию с подсветкой
        prefetch_products = Prefetch(
            "products_quantity",
            queryset=Poducts_in_palet_quantity.objects.select_related("product").annotate(
                highlighted_name=headline
            ),
        )

    # Предварительно загружаем связанные данные, используя наш prefetch
    palets = palets_qs.order_by("number").distinct().prefetch_related(prefetch_products)

    # Получаем ID паллет для кнопки печати
    palet_ids = list(palets.values_list("id", flat=True))

    return render(
        request,
        "pallets/palet_list.html",
        {"palets": palets, "search": search_query, "palet_ids": palet_ids},
    )


def send_palet(request, palet_id):
    if request.method == "POST":
        try:
            palet = get_object_or_404(Palet, id=palet_id)

            # Получаем список продуктов в паллете с количеством
            products_list = []
            for product_quantity in palet.products_quantity.all():
                products_list.append(
                    f"{product_quantity.product.product_name} - {product_quantity.quantity} шт."
                )
            # Формируем HTML-версию с правильными тегами
            products_html = "<br>".join(products_list)

            payload = {
                "text": f"Паллета № {palet.number}",
                "textHtml": f"<p>Паллета {palet.number}<br>Содержимое:<br>{products_html}</p>",
                "label": f"Паллета № {palet.number} {time.strftime('%d.%m.%Y %H:%M')}",
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {os.getenv('YOUGILE_API_KEY')}",
            }

            url = f"https://ru.yougile.com/api-v2/chats/{os.getenv('YOUGILE_CHAT_ID')}/messages"

            response = requests.request("POST", url, json=payload, headers=headers)

            try:
                response.raise_for_status()
                messages.success(request, f"Паллета №{palet.number} успешно заказана!")

                # Отправка сообщения в Telegram
                # telegram_message = (
                #     f"Паллета №{palet.number}.\n"
                #     f"Содержимое:\n{products_text}"
                # )
                # # Укажите свой username или user_id
                # asyncio.run(send_telegram_message('Ninila_company', telegram_message))

                # Помечаем паллету как полученную после успешной отправки
                palet.receipt_mark = True
                palet.save()
            except requests.exceptions.HTTPError as e:
                messages.error(request, f"Ошибка при заказе паллеты №{palet.number}: {str(e)}")

            return HttpResponseRedirect(reverse("pallets:palet_list"))

        except Exception as e:
            messages.error(request, f"Произошла ошибка: {str(e)}")
            return HttpResponseRedirect(reverse("pallets:palet_list"))


def print_palets_pdf(request):
    if request.method == "POST":
        palet_ids = request.POST.getlist("palet_ids")
        if not palet_ids:
            messages.warning(request, "Нет паллет для печати.")
            return HttpResponseRedirect(reverse("pallets:palet_list"))

        try:
            from weasyprint import HTML

            palets = Palet.objects.filter(id__in=palet_ids).prefetch_related(
                "products_quantity__product"
            )
            context = {
                "palets": palets,
                "generation_time": timezone.now(),
            }
            html_string = render_to_string("pallets/print_selected_palets.html", context)

            pdf_file = HTML(string=html_string).write_pdf()

            response = HttpResponse(pdf_file, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="pallets.pdf"'
            return response
        except Exception as e:
            messages.error(request, f"Ошибка при генерации PDF: {str(e)}")

    return HttpResponseRedirect(reverse("pallets:palet_list"))
