from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls), 

    # API v1 Routes
    path('api/v1/', include('config.api_urls')), 

    # Auto-generated API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'), 
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema') ,name='docs'), 

    # Path for reports
    path('reports/', include('apps.reports.urls')), 
]