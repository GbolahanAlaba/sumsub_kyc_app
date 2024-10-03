from django.contrib.auth.models import User
from . models import *
from rest_framework.response import Response
from rest_framework import serializers, validators



class VerificationSerializer(serializers.ModelSerializer):

    class Meta:
        model = VerificationStatus
        fields = ['applicant_id', 'country', 'id_doc_type', 'image_ids', 
                  'image_review_results', 'forbidden', 'partial_completion', 
                  'step_statuses', 'image_statuses', 'selfie']