"""
URL configuration for AbsoluteCinemaProject project.
"""

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('rango.urls')),
    path('admin/', admin.site.urls),
]