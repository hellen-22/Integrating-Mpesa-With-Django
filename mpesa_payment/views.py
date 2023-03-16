import json

from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.http import HttpResponse
#from django_daraja.mpesa.core import MpesaClient
from .utils import MpesaGateWay
from .validators import *


from .models import *

cl = MpesaGateWay()

def mpesa_payment(request):
    if request.method == 'POST':
        phone_number = request.POST['phone_number']
        amount = int(request.POST['amount'])
        account_reference = 'Reference'
        transaction_desc = 'Description'
        callback_url = request.build_absolute_uri(reverse('callback'))

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

@csrf_exempt
def stk_push_callback(request, *args, **kwargs):
    if request.method == 'POST':
        pass

    if request.method == 'GET':
        body_unicode = request.body.decode('utf-8')
        

        if body_unicode == '':
            return HttpResponse('No response')
        
        else:
            body = json.loads(body_unicode)
            print(body)
            if body['Body']['stkCallback']['ResultCode'] == 0:
                payment = TransactionCallbacks(
                    checkout_request_id = body['Body']['stkCallback']['CheckoutRequestID'],
                    merchant_request_id = body['Body']['stkCallback']['MerchantRequestID'],
                    amount = body['Body']['stkCallback']['CallbackMetadata']['Item'][0]["Value"],
                    mpesa_receipt_no = body['Body']['stkCallback']['CallbackMetadata']['Item'][1]["Value"],
                    phone_number = body['Body']['stkCallback']['CallbackMetadata']['Item'][-1]["Value"],
                )
                payment.save()
                messages.success(request, 'Successfully Paid')
                return HttpResponse(body)  
            else:
                messages.error(request, 'Transaction Declined By User')
                
    return HttpResponse()

def method_test(request):
    print(f'This is {request.method}')
    return HttpResponse('This is method test')