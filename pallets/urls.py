from django.urls import path

from . import views

app_name = "pallets"

urlpatterns = [
    path("", views.palet_list, name="palet_list"),
    path("palet/<int:palet_id>/send/", views.send_palet, name="send_palet"),
    path("print-pdf/", views.print_palets_pdf, name="print_palets_pdf"),
]
