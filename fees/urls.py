from django.urls import path

from . import views


urlpatterns = [
    path(
        "heads/",
        views.fee_head_list,
        name="fee_head_list",
    ),

    path(
        "heads/add/",
        views.fee_head_create,
        name="fee_head_create",
    ),

    path(
        "concessions/",
        views.concession_list,
        name="concession_list",
    ),

    path(
        "concessions/add/",
        views.concession_create,
        name="concession_create",
    ),

    path(
        "concessions/<int:pk>/",
        views.concession_detail,
        name="concession_detail",
    ),

    path(
        "concessions/<int:pk>/approve/",
        views.concession_approve,
        name="concession_approve",
    ),

    path(
        "concessions/<int:pk>/reject/",
        views.concession_reject,
        name="concession_reject",
    ),

    path(
        "concessions/<int:pk>/cancel/",
        views.concession_cancel,
        name="concession_cancel",
    ),

    path(
    "invoices/",
    views.invoice_list,
    name="invoice_list",
    ),

    path(
        "invoices/add/",
        views.invoice_create,
        name="invoice_create",
    ),

    path(
        "invoices/<int:pk>/",
        views.invoice_detail,
        name="invoice_detail",
    ),
]