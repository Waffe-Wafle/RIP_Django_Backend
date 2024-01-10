from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter


# All abilities encapsulated:
router = DefaultRouter()
router.register('softs',    SoftViewSet)
router.register('payments', PaymentViewSet)
router.register('files', FileViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('manage_payment_status/',                  PaymentStatusUserView.as_view()),
    path('manage_payment_status_admin/<int:pk>/', PaymentStatusAdminView.as_view()),
    path('manage_payment_soft/',                  PaymentSoftView.as_view())
]
