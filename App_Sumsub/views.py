from django.shortcuts import render
from rest_framework.response import Response
from . models import VerificationStatus
from . serializers import VerificationSerializer
import requests
import json
from rest_framework import viewsets, status
from rest_framework.decorators import action
from django.conf import settings
from functools import wraps
from decouple import config
import hashlib
import hmac
import json
import time
import logging

def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_message = str(e)
            return Response({"status": "failed", "message": error_message}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return wrapper


class SumsubViewSet(viewsets.ViewSet):
    
    @handle_exceptions
    def sign_request(self, request: requests.Request) -> requests.PreparedRequest:
        prepared_request = request.prepare()
        now = int(time.time())
        method = request.method.upper()
        path_url = prepared_request.path_url  # includes encoded query params
        body = b'' if prepared_request.body is None else prepared_request.body
        if isinstance(body, str):
            body = body.encode('utf-8')

        data_to_sign = str(now).encode('utf-8') + method.encode('utf-8') + path_url.encode('utf-8') + body

        signature = hmac.new(
            settings.SUMSUB_SECRET_KEY.encode('utf-8'),
            data_to_sign,
            digestmod=hashlib.sha256
        )

        prepared_request.headers['X-App-Token'] = settings.SUMSUB_TOKEN
        prepared_request.headers['X-App-Access-Ts'] = str(now)
        prepared_request.headers['X-App-Access-Sig'] = signature.hexdigest()
        return prepared_request


    @handle_exceptions
    @action(detail=False, methods=['post'])
    def create_applicant(self, request):
        external_user_id = request.data.get('externalUserId')
        info = request.data.get('info')
        type = request.data.get('type')
        level_name = request.data.get('levelName', 'basic-kyc-level')  # Default to 'basic-kyc-level'

        if not external_user_id:
            return Response({"status": "failed", "message": "externalUserId is required"}, status=status.HTTP_400_BAD_REQUEST)

        payload = {
            "externalUserId": external_user_id,
            "info": info,
            "type": type,
        }

        url = f"https://api.sumsub.com/resources/applicants?levelName={level_name}"
        headers = {'Content-Type': 'application/json'}
        request_obj = requests.Request('POST', url, headers=headers, json=payload)

        signed_request = self.sign_request(request_obj)

        response = requests.Session().send(signed_request)
        
        if response.status_code == 201:
            return Response({"status": "success", "message": "Applicant created successfully", "data": response.json()}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "failed", "message": response.json()}, status=response.status_code)
        

    @handle_exceptions
    @action(detail=True, methods=['post'])
    def add_document(self, request, pk=None):
        
        """Add a document to the applicant."""
        applicant_id = pk
        img_url = request.data.get('img_url')
        id_doc_type = request.data.get('idDocType')
        country = request.data.get('country')

        if not img_url or not id_doc_type or not country:
            return Response({"status": "failed", "message": "img_url, idDocType, and country are required"}, status=status.HTTP_400_BAD_REQUEST)

        """Download the image"""
        try:
            img_response = requests.get(img_url, stream=True, timeout=settings.REQUEST_TIMEOUT)
            img_response.raise_for_status()

            """Save the image temporarily"""
            img_file_path = 'images/img.jpg'
            with open(img_file_path, 'wb') as handle:
                for block in img_response.iter_content(1024):
                    if not block:
                        break
                    handle.write(block)

            metadata = {
                "idDocType": id_doc_type,
                "country": country
            }

            url = f"https://api.sumsub.com/resources/applicants/{applicant_id}/info/idDoc"
            request_obj = requests.Request(
                'POST', 
                url, 
                files={'content': open(img_file_path, 'rb')},  # Open the image file
                data={'metadata': json.dumps(metadata)}  # Send metadata as a string
            )

            signed_request = self.sign_request(request_obj)
            response = requests.Session().send(signed_request)
            if response.status_code == 200:
                return Response({"status": "success", "message": "Document added successfully", "data": response.json()}, status=response.status_code)
            else:
                return Response({"status": "failed", "message": response.json()}, status=response.status_code)

        except Exception as e:
            logging.error(f"Error while adding document: {str(e)}")
            return Response({"status": "failed", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
    @handle_exceptions
    @action(detail=True, methods=['get'])
    def get_applicant_verification_status(self, request, pk=None):
        """
        Get the status of an applicant using the applicant ID.
        """
        applicant_id = pk
        if not applicant_id:
            return Response({"status": "failed", "message": "Applicant ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        SUMSUB_TEST_BASE_URL = "https://api.sumsub.com"
        url = f"{SUMSUB_TEST_BASE_URL}/resources/applicants/{applicant_id}/requiredIdDocsStatus"
        request_obj = requests.Request('GET', url)
        signed_request = self.sign_request(request_obj)
        response = requests.Session().send(signed_request)
        
        if response.status_code == 200:
            data = response.json()

            """ Extract identity_data directly from the top-level response """
            identity_data = data.get("IDENTITY", {})
            selfie_data = data.get("SELFIE", None)

            """Extract values from the verification status"""
            country = identity_data.get("country", "Unknown")
            id_doc_type = identity_data.get("idDocType", "Unknown")
            image_ids = identity_data.get("imageIds", [])
            image_review_results = identity_data.get("imageReviewResults", {})
            forbidden = identity_data.get("forbidden", False)
            partial_completion = identity_data.get("partialCompletion", None)
            step_statuses = identity_data.get("stepStatuses", None)
            image_statuses = identity_data.get("imageStatuses", [])

            """ Create or update the verification status in the database """
            verification_status, created = VerificationStatus.objects.update_or_create(
                applicant_id=applicant_id,
                defaults={
                    'country': country,
                    'id_doc_type': id_doc_type,
                    'image_ids': image_ids,
                    'image_review_results': image_review_results,
                    'forbidden': forbidden,
                    'partial_completion': partial_completion,
                    'step_statuses': step_statuses,
                    'image_statuses': image_statuses,
                    'selfie': json.dumps(selfie_data) if selfie_data else None,
                }
            )
            return Response({"status": "success", "message": f"Verification status for: {applicant_id}", "data": data}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "failed", "message": "Error fetching data from Sumsub."}, status=response.status_code)


    @handle_exceptions
    @action(detail=True, methods=['get'])
    def get_saved_verification_data(self, request, pk=None):

        applicant_id = pk
        if not applicant_id:
            return Response({"status": "failed", "message": "Applicant ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        elif not VerificationStatus.objects.filter(applicant_id=applicant_id).first():
            return Response({"status": "failed", "message": "Applicant not found"}, status=status.HTTP_404_NOT_FOUND)
        else:
            applicant = VerificationStatus.objects.get(applicant_id=applicant_id)
            serializer = VerificationSerializer(applicant)
            print(applicant)
            return Response({"status": "success", "message": f"Verification data for applicant {applicant_id}", "data": serializer.data}, status=status.HTTP_200_OK)

