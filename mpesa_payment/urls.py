from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register("callback", views.MpesaViewSet, basename="callback")

urlpatterns = [
    path('', views.mpesa_payment, name='mpesa'),
    #path('callback', views.stk_push_callback, name='callback'),
    path('transaction', views.saving_transactions, name='transactions'),
    path("", include(router.urls))
]
