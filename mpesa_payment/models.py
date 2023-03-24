from django.db import models
from django.core.validators import MinValueValidator


class AbstractBaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract =True


class TransactionCallbacks(AbstractBaseModel):
    phone_number = models.CharField(max_length=100)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    received_at = models.DateTimeField(auto_now_add=True)
    checkout_request_id = models.CharField(max_length=255)
    merchant_request_id = models.CharField(max_length=255)
    mpesa_receipt_no = models.CharField(max_length=255)

    def __str__(self) -> str:
        return self.phone_number
    
    class Meta:
        verbose_name = 'Transaction'
    

class MpesaResponseBody(AbstractBaseModel):
    body = models.JSONField()

    def __str__(self) -> str:
        return str(self.body)