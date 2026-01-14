from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("account/status", views.login, name="status"),
    path("account/login", views.login, name="login"),
]
