from django.urls import path, include
from django.contrib import admin
from .views import index

from django.conf.urls.static import static
from .settings import MEDIA_URL, MEDIA_ROOT


urlpatterns = [
    path('django_templates/', include('SoftLoading.urls', namespace='soft_loading')),
    path('admin/',            admin.site.urls),
    path('', index),

]


urlpatterns += static(MEDIA_URL, document_root=MEDIA_ROOT)