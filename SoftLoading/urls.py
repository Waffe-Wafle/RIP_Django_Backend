from django.urls import path
from .views import *


app_name = 'SoftLoading'
urlpatterns = [
    path('catalog/', catalog,   name='catalog'),
    path('soft/<int:soft_id>/', soft, name='soft'),
]
