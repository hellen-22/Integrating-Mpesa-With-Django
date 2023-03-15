from django.urls import path
from . import views

urlpatterns = [
    path('', views.mpesa_payment, name='mpesa'),
    path('callback', views.stk_push_callback, name='callback'),
    path('method', views.method_test, name='method'),
]