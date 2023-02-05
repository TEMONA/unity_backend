from django.contrib import admin
from django.urls import path
from django.conf.urls import include
from django.conf.urls.static import static
from django.conf import settings
from django.views.generic import TemplateView
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import OpenAPIRenderer
from rest_framework import permissions

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('basicapi.urls')),
    path('authen/', include('djoser.urls')),
    path('authen/', include('djoser.urls.jwt')),
    path('openapi-schema/', get_schema_view(
        title="title",
        description="title",
        version="1.0.0",
        public=True,
        # urlconf='basicapi.urls',
        # renderer_classes=[OpenAPIRenderer],
        permission_classes=(permissions.AllowAny,),
    ), name='openapi-schema'),
    path('docs/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
    path('kaonavi-api/', include('kaonaviapi.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
