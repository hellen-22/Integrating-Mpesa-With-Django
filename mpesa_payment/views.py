import json
import requests

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponse
#from django_daraja.mpesa.core import MpesaClient
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status

from .utils import MpesaGateWay
from .validators import *
from .serializers import MpesaResponseBodySerializer
from .models import *

cl = MpesaGateWay()

def mpesa_payment(request):
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        amount = int(request.POST['amount'])
        account_reference = 'Ocrat POS Payment'
        transaction_desc = 'Payment'
        callback_url = "https://mpesa.ocratsystems.co.ke/callback/"

        print(callback_url)
        print(type(phone_number))

        if phone_number[0] == "+":
            phone_number = phone_number[1:]
        if phone_number[0] == "0":
            phone_number = "254" + phone_number[1:]
        try:
            validate_possible_number(phone_number, "KE")
        except:
            messages.info(request, 'Phone number is invalid')
            return redirect('mpesa')
        
        if not amount or amount <= 0:
            messages.info(request, 'Amount should be greater that 0')
            return redirect('mpesa')

        response = cl.stk_push(phone_number=phone_number, amount=amount, account_reference=account_reference, transaction_desc=transaction_desc, callback_url=callback_url)


        if response.status_code == 200:
            return redirect("success")
        
        return redirect("failed")

    else:
        return render(request, 'mpesa.html')



def saving_transactions(request):
    transactions = TransactionCallbacks.objects.all()

    context = {
        "transactions": transactions
    }

    return render(request, 'response.html', context)


def successful_redirect(request):
    return render(request, "success.html")


def failed_redirect(request):
    return render(request, "failed.html")



class MpesaViewSet(ModelViewSet):
    queryset = MpesaResponseBody.objects.all()
    serializer_class = MpesaResponseBodySerializer

    

    