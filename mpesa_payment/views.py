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
        callback_url = ""

        print(callback_url)

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
        
        return HttpResponse(response)


    else:
        return render(request, 'mpesa.html')



def saving_transactions(request):
    transactions = TransactionCallbacks.objects.all()

    context = {
        "transactions": transactions
    }

    return render(request, 'response.html', context)



class MpesaViewSet(ModelViewSet):
    queryset = MpesaResponseBody.objects.all()
    serializer_class = MpesaResponseBodySerializer

    def create(self, request, *args, **kwargs):
        body = request.data["Body"]
        print("***************Callback Data***************")
        print(body)
        print("***************Callback Data***************")

        if body:
            mpesa = MpesaResponseBody.objects.create(body=body)

            # mpesa_body = mpesa.body

            # if mpesa_body['stkCallback']['ResultCode'] == 0:
            #     payment = TransactionCallbacks(
            #         checkout_request_id = mpesa_body['stkCallback']['CheckoutRequestID'],
            #         merchant_request_id = mpesa_body['stkCallback']['MerchantRequestID'],
            #         amount = mpesa_body['stkCallback']['CallbackMetadata']['Item'][0]["Value"],
            #         mpesa_receipt_no = mpesa_body['stkCallback']['CallbackMetadata']['Item'][1]["Value"],
            #         phone_number = mpesa_body['stkCallback']['CallbackMetadata']['Item'][-1]["Value"],
            #     )
            #     payment.save()
                  
            # else:
            #     pass

            return Response({"message": "Transaction Successful!!"}, status=status.HTTP_201_CREATED)
        return Response({"failed": "Transaction Failed"}, status=status.HTTP_400_BAD_REQUEST)

