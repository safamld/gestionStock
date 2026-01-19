"""
URL configuration for gestion_stock project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.decorators.http import require_http_methods
from stock.views import login_view, logout_view, agent_dashboard

urlpatterns = [
    # Routes d'authentification (avant admin)
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', agent_dashboard, name='agent_dashboard'),
    # Route par défaut: redirection vers login
    path('', login_view, name='home'),
    
    # Admin moderne avec Grappelli
    # path('grappelli/', include('grappelli.urls')),  # À installer: pip install django-grappelli
    path('admin/', admin.site.urls),
    
    # Routes pour l'application stock
    path('stock/', include('stock.urls')),
]

# Servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
