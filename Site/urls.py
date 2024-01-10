from django.urls import path, include
from django.contrib import admin
from .views import index


urlpatterns = [
    path('api/soft_loading_api/v1/', include('SoftLoading.api_v1.urls')),
    path('django_templates/',    include('SoftLoading.urls', namespace='soft_loading')),
    path('admin/',               admin.site.urls),
    path('', index),
]