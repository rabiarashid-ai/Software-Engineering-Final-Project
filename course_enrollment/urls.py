from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.urls import include, path

urlpatterns = [
    path("admin/logout/", LogoutView.as_view(next_page="/admin/login/?next=/admin/"), name="admin_logout"),
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", include("enrollment.urls")),
]
