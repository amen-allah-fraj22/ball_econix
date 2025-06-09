"""
URL configuration for economic_platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# backend/economic_platform/economic_platform/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from authentication import views as authentication_views # Removed this import as authentication.urls will handle all auth paths
from django.views.generic.base import RedirectView # Import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/analytics/', include('analytics.urls', namespace='analytics_api')),
    path('countries/', include('countries.urls')),

    # Include authentication urls under a distinct path for all auth-related views (template and API)
    path('auth/', include('authentication.urls', namespace='auth')),
    path('api/governorates/', include('governorates.urls')),

    # Add frontend URLs
    path('', include('frontend.urls')),

    # Redirect root to login page
    path('', RedirectView.as_view(url='/auth/login/', permanent=False)),
]

# Serve static files during development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)