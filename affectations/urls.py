from django.urls import path
from . import views


app_name = "affectations"

urlpatterns = [
    path("", views.affectation_list, name="list"),
    path("detail/<path:pk>/", views.affectation_detail, name="detail"),
    path("delete/", views.affectation_delete, name="delete"),
    path("ajouter/", views.affectation_start, name="start"),
    path("choisir-agent/", views.affectation_choose_agent, name="choose_agent"),
    path("choisir-type/", views.affectation_choose_type, name="choose_type"),
    path("step1/", views.affectation_step1, name="step1"),
    path("step2/", views.affectation_step2, name="step2"),
    path("pdf/<path:pk>/", views.affectation_pdf, name="pdf"),
    path("docx/<path:pk>/", views.affectation_docx, name="docx"),
]
