from django.shortcuts import render
from rest_framework.response import Response
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
import requests
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

        body = {
            "externalUserId": external_user_id,
            "info": info,
            "type": type,
        }

        url = f"https://api.sumsub.com/resources/applicants?levelName={level_name}"
        headers = {'Content-Type': 'application/json'}
        request_obj = requests.Request('POST', url, headers=headers, json=body)

        signed_request = self.sign_request(request_obj)

        response = requests.Session().send(signed_request)
        
        if response.status_code == 200:
            return Response({"status": "success", "message": "applicant created successfully", "data": response.json()}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": "failed", "message": response.json()}, status=response.status_code)

    @action(detail=True, methods=['post'])
    def add_document(self, request, pk=None):
        """Add a document to the applicant."""
        applicant_id = pk
        img_url = request.data.get('img_url')
        id_doc_type = request.data.get('idDocType')
        country = request.data.get('country')

        if not img_url or not id_doc_type or not country:
            return Response({"status": "failed", "message": "img_url, idDocType, and country are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            img_response = requests.get(img_url, stream=True, timeout=settings.REQUEST_TIMEOUT)
            img_response.raise_for_status()

            img_file_path = 'img.jpg'
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


    @action(detail=True, methods=['get'])
    def get_applicant_status(self, request, pk=None):
        """
        Get the status of an applicant using the applicant ID.
        """
        if not pk:
            return Response({"status": "failed", "message": "Applicant ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        SUMSUB_TEST_BASE_URL = "https://api.sumsub.com"
        url = f"{SUMSUB_TEST_BASE_URL}/resources/applicants/{pk}/requiredIdDocsStatus"
        request_obj = requests.Request('GET', url)

        signed_request = self.sign_request(request_obj)

        response = requests.Session().send(signed_request)
        
        if response.status_code == 200:
            return Response({"status": "success", "message": f"Verification status for: {pk}", "data": response.json()}, status=status.HTTP_200_OK)
        else:
            return Response({"status": "failed", "message": response.json()}, status=response.status_code)







# class SumsubApplicantViewSet(viewsets.ViewSet):

#     def create_applicantt(self, request):
#         base_url = "https://api.sumsub.com"
#         level_name = "basic-kyc-level"
#         url = f"/resources/applicants?levelName={level_name}"
#         full_url = base_url + url

#         timestamp = str(int(time.time()))  # Ensure accurate timestamp
#         print("Timestamp: ", timestamp)

#         secret_key = settings.SUMSUB_SECRET_KEY.strip()  # Strip any extra spaces

#         # Request body, ensure it's properly structured
#         request_body = {
#             'externalUserId': '675767449',
#             'type': 'individual',
#             'info': {
#                 'companyInfo': {
#                     'address': {
#                         'street': 'Sola Makidne',
#                         'postCode': '100275'
#                     },
#                     'companyName': 'Expedier',
#                     'registrationNumber': 'BC123456',
#                     'country': 'Nigeria',
#                     'legalAddress': '3, Ajilekege Street, Idimu'
#                 }
#             }
#         }

#         # Minified body
#         request_body_str = json.dumps(request_body, separators=(',', ':'))

#         # String to Sign
#         string_to_sign = timestamp + 'POST' + url + request_body_str
#         print("String to Sign (minified): ", string_to_sign)

#         # Generate HMAC-SHA256 signature
#         signature = hmac.new(
#             secret_key.encode('utf-8'),
#             string_to_sign.encode('utf-8'),
#             hashlib.sha256
#         ).hexdigest()

#         # Debug: Print the generated signature
#         print("Generated Signature: ", signature)

#         headers = {
#             "content-type": "application/json",
#             "X-App-Token": settings.SUMSUB_TOKEN,
#             "X-App-Access-Sig": signature,
#             "X-App-Access-Ts": timestamp,
#             "Content-Encoding": "utf-8"
#         }

#         # Debug: Print headers
#         print("Headers: ", headers)

#         try:
#             # Send the request
#             response = requests.post(full_url, headers=headers, json=request_body)
#             print("Response: ", response.text)  # Debug response body
#             if response.status_code == 200 or response.status_code == 201:
#                 return Response(response.json(), status=status.HTTP_201_CREATED)
#             else:
#                 return Response({"status": "failed", "message": response.text}, status=status.HTTP_400_BAD_REQUEST)
#         except requests.exceptions.RequestException as e:
#             return Response({"status": "failed", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


#     def add_applicant_ID(self, request):
#         url = "https://api.sumsub.com/resources/applicants/347484838/info/idDoc"
#         headers = {
#             "X-Return-Doc-Warnings": "true",
#             "content-type": "application/json",
#             "X-App-Token": "sbx:ur4J0kqKD2sVo8tems6Ssiwx.4ZUkY5JbgVkPgYE6XU3ptFb7lrFrK8If"
#         }

#         try:
#             response = requests.post(url, headers=headers)
#             if response.status_code == 200 or response.status_code == 201:
#                 return Response(response.json(), status=status.HTTP_201_CREATED)
#                 print(response.text)
#             else:
#                 return Response({"status": "failed", "message": response.text}, status=status.HTTP_400_BAD_REQUEST)
#         except requests.exceptions.RequestException as e:
#             return Response({"status": "failed", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
# class SumsubViewSets(viewsets.ViewSet):
        
#     @handle_exceptions
#     def get_header(self):
#         return {
#             'Content-Type': 'application/json',
#             'X-App-Token': settings.SUMSUB_TOKEN,
#         }

#     @handle_exceptions
#     def initiate_applicant(self, externalUserId, type, companyInfo):
#         url = "https://api.sumsub.com/resources/applicants?levelName=basic-kyc-level"
#         payload = json.dumps({
#             "externalUserId": externalUserId,
#             "type": type,
#             "info": {
#                 "companyInfo": companyInfo
#             }
#         })

#         headers = self.get_header()
#         try:
#             response = requests.post(url, headers=headers)
#             print("Sumsub Response:", response.text)

#             response.raise_for_status()
#             response_data = response.json()
#             return response_data

#         except requests.exceptions.HTTPError as http_err:
#             print(f"HTTP error occurred: {http_err}")
#             return {"status": "failed", "message": f"HTTP error occurred: {http_err}"}

#     @handle_exceptions
#     def create_applicant(self, request):
#         externalUserId = request.data.get('externalUserId')
#         type = request.data.get('type')
#         companyInfo = request.data.get('info')
#         try:
#             applicant_response = self.initiate_applicant(externalUserId, type, companyInfo)
#             if not applicant_response or 'error' in applicant_response:
#                 error_message = applicant_response.get({"status": "failed", "message": "No data returned from Sumsub"})
#                 return Response({"status": "failed", "message": error_message}, status=status.HTTP_400_BAD_REQUEST)
            
#             serializer = SumsubSerializer(applicant_response)
#             return Response({"status": "success", "message": "Applicant created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({"status": "failed", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# class SumsubViewSetsD(viewsets.ViewSet):

    # @handle_exceptions
    # def get_header(self):
    #     return {
    #     'Content-Type': 'application/json',
    #     'X-App-Token' : f'{settings.SUMSUB_SECRET_KEY}',
    #     }
    
    # @handle_exceptions
    # def initiate_applicant(self, sourceKey, email, phone, type):
    #     url = "https://api.sumsub.com/resources/applicants"

    #     payload = json.dumps({
    #     "sourceKey": sourceKey,
    #     "email": email,
    #     "phone": phone,
    #     "type": type,
    #     })

    #     headers = self.get_header()
    #     response = requests.request("POST", url, headers=headers, data=payload)
     
    #     response_data = response.json()
    #     return response_data

    # @handle_exceptions
    # def create_applicant(self, request):
    #     sourceKey = request.data.get('sourceKey')
    #     email = request.data.get('email')
    #     phone = request.data.get('phone')
    #     type = request.data.get('type')
    
    #     try:
    #         applicant_response = self.initiate_applicant(sourceKey, email, phone, type)
    #         if not applicant_response:  # Check if the response is empty
    #             return Response({"status": "failed", "message": "No data returned from Sumsub"}, status=status.HTTP_400_BAD_REQUEST)
            
    #         serializer = SumsubSerializer(applicant_response)
    #         return Response({"status": "success", "message": "Applicant created successfully", "data": serializer.data}, status=status.HTTP_201_CREATED)
    #     except Exception as e:
    #         return Response({"status": "failed", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

        







  # if response.status_code == 200:
        #     return response.json()  # Convert response to JSON
        # else:
        # # Handle error appropriately
        #     return {"status": "failed", "message": "Failed to create applicant", "details": response.text}