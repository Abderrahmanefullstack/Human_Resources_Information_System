# vivier/urls.py
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = "vivier"

urlpatterns = [
    path("", views.vivier_list, name="list"),
    path("ajouter/", views.vivier_create, name="create"),
    path(
        "<int:pk>/export-agents/", views.export_agents_excel, name="export_agents_excel"
    ),
    path("<int:pk>/modifier/", views.vivier_update, name="update"),
    path(
        "<int:vivier_id>/commission/<str:matricule>/",
        views.commission_edit,
        name="commission_edit",
    ),
    path("<int:pk>/supprimer/", views.vivier_delete, name="delete"),
    path("<int:pk>/pj/", views.download_pj, name="download_pj"),
    path(
        "<int:pk>/piece/<int:piece_id>/supprimer/",
        views.vivier_piece_delete,
        name="piece_delete",
    ),
    path(
        "<int:vivier_id>/commission/<str:matricule>/imprimer/",
        views.commission_print,
        name="commission_print",
    ),
    path("<int:pk>/pv-non-traj/", views.vivier_pv_non_traj, name="pv_non_traj"),
    path("<int:pk>/debug-grid/", views.vivier_pv_debug_grid, name="pv_debug_grid"),
]
