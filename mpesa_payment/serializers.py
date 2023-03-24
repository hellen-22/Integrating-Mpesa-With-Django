from .models import MpesaResponseBody
from rest_framework import serializers

class MpesaResponseBodySerializer(serializers.ModelSerializer):
    class Meta:
        model = MpesaResponseBody
        fields = "__all__"