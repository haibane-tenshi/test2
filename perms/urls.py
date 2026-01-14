from django.urls import path

from . import views

urlpatterns = [
    path("", views.index),
    path("account/status", views.status, name="status"),
    path("account/login", views.login, name="login"),
    path("account/logout", views.logout, name="logout"),
    path("test/a", views.test_a),
    path("test/b", views.test_b),
    path("test/c", views.test_c),
]
