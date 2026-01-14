from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("account/status", views.status, name="status"),
    path("account/login", views.login, name="login"),
    path("account/logout", views.logout, name="logout"),
]
