from django.contrib import admin
from django.urls import include, path
from users.views import home  # Optionnel si tu veux garder ici la racine
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("users.urls")),  # inclut login, logout, home
    path("agents/", include("agents.urls", namespace="agents")),
    path("fonctions/", include("fonctions.urls")),
    path("entites/", include("entites.urls")),
    path("affectations/", include("affectations.urls")),
    path("vivier/", include("vivier.urls")),
    path("annonces/", include(("annonces.urls", "annonces"), namespace="annonces")),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
