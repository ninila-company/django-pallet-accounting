import os
import time

import requests
from django.contrib import messages, postgres

# from django.db.models import Q
from django.db.models import Prefetch
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

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

    return render(request, "pallets/palet_list.html", {"palets": palets, "search": search_query})


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
            products_text = "\n".join(products_list)

            payload = {
                "text": f"Паллета № {palet.number}",
                "textHtml": f"<p>Паллета {palet.number}\nСодержимое:\n{products_text}</p>",
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
