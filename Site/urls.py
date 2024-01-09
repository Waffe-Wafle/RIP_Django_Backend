from django.urls import path, include
from .views import index


urlpatterns = [
    path('django_templates/', include('SoftLoading.urls', namespace='soft_loading')),
    path('', index),
]

