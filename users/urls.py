from django.urls import path
from .views import login_view, logout_view, home, CustomLoginView
from django.conf.urls.static import static
from django.conf import settings

app_name = "users"

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
    path("", home, name="home"),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
