import os
import time

import requests
from django.contrib import messages
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from dotenv import load_dotenv

from .models import Palet

load_dotenv()


def palet_list(request):
    search_query = request.GET.get("search", "").strip()

    # Начинаем с базового запроса
    palets_qs = Palet.objects.filter(receipt_mark=False)

    if search_query:
        words = search_query.split()
        q_objects = Q()
        for word in words:
            # Логика И для слов
            q_objects &= Q(products_quantity__product__product_name__icontains=word)
        palets_qs = palets_qs.filter(q_objects)

    # Предварительно загружаем связанные данные, чтобы избежать N+1 запросов в шаблоне
    palets = (
        palets_qs.order_by("number")
        .distinct()
        .prefetch_related("products_quantity__product")
    )

    return render(
        request, "pallets/palet_list.html", {"palets": palets, "search": search_query}
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
                messages.error(
                    request, f"Ошибка при заказе паллеты №{palet.number}: {str(e)}"
                )

            return HttpResponseRedirect(reverse("pallets:palet_list"))

        except Exception as e:
            messages.error(request, f"Произошла ошибка: {str(e)}")
            return HttpResponseRedirect(reverse("pallets:palet_list"))
