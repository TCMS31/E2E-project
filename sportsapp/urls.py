"""Root URL configuration."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('sports.urls')),
]

# Custom error pages. Django reads these module-level names after the URLconf
# is imported; they only take effect when DEBUG is off.
handler404 = 'sports.views.custom_404_view'
handler500 = 'sports.views.custom_500_view'
