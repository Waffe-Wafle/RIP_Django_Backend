from django.urls import path, include
from django.contrib import admin
from .views import index

from drf_yasg.views import get_schema_view
from drf_yasg.openapi import Info, Contact, License
from rest_framework.permissions import AllowAny


schema_view = get_schema_view(
   Info(
      title="Snippets API",
      default_version='v1',
      description="Test description",
      terms_of_soft="https://www.google.com/policies/terms/",
      contact=Contact(email="contact@snippets.local"),
      license=License(name="BSD License"),
   ),
   public=True,
   permission_classes=[AllowAny]
)


urlpatterns = [
    path('api/soft_loading_api/v1/', include('SoftLoading.api_v1.urls')),
    path('api/profiles_api/v1/',     include('Profiles.api_v1.urls')),
    path('django_templates/',    include('SoftLoading.urls', namespace='soft_loading')),
    path('admin/',               admin.site.urls),
    path('', index),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui')
]
