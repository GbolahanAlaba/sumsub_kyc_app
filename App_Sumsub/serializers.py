from django.contrib.auth.models import User
from . models import *
from rest_framework.response import Response
from rest_framework import serializers, validators



class VerificationSerializer(serializers.Serializer):

    class Meta:
        model = VerificationStatus
        fields = '__all__'