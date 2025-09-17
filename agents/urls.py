from django.urls import path
from . import views
from agents.views import (
    agent_detail,
    agent_update,
    agent_delete,
    agent_list,
    download_template,
    import_excel,
    export_excel,
)


app_name = "agents"

urlpatterns = [
    path("", views.agent_list, name="list"),
    path("importer-excel/", views.import_excel, name="import_excel"),
    path("telecharger-modele/", views.download_template, name="download_template"),
    path("purger-agents/", views.purge_agents, name="purge_agents"),
    path("export/", views.export_excel, name="export_excel"),
    # URLs for agent detail, update, and delete
    path("<str:pk>/", views.agent_detail, name="view"),
    path("<str:pk>/modifier/", views.agent_update, name="edit"),
    path("<str:pk>/supprimer/", views.agent_delete, name="delete"),
]
