# annonces/urls.py
from django.urls import path
from . import views

app_name = "annonces"

urlpatterns = [
    path("", views.annonce_list, name="list"),
    path("ajouter/", views.annonce_create, name="create"),
    path("<int:pk>/modifier/", views.annonce_update, name="update"),
    path("<int:pk>/supprimer/", views.annonce_delete, name="delete"),
]
