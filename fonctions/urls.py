from django.urls import path
from . import views
from fonctions.views import (
    fonction_list,
    import_excel,
    download_template,
    fonction_detail,
    fonction_delete,
    fonction_update,
    export_excel,  # 👈 à importer aussi
)

app_name = "fonctions"

urlpatterns = [
    path("", views.fonction_list, name="list"),
    path("import/", views.import_excel, name="import_excel"),
    path("template/", views.download_template, name="download_template"),
    path("export/", views.export_excel, name="export_excel"),  # 👈 ajout
    path("<str:code>/modifier/", views.fonction_update, name="update"),
    path("<str:code>/supprimer/", views.fonction_delete, name="delete"),
    path("<str:code>/", views.fonction_detail, name="detail"),
]
