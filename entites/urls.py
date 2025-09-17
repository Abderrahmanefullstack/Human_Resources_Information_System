from django.urls import path
from . import views

app_name = "entites"

urlpatterns = [
    path("", views.entite_list, name="list"),
    path("detail/", views.entite_detail, name="detail"),
    path("create/", views.entite_create, name="create"),
    path("update/", views.entite_update, name="update"),
    path("delete/", views.entite_delete, name="delete"),
]
