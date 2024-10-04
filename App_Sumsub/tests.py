from django.urls import reverse, resolve
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.test import TestCase
from . models import *
from . views import SumsubViewSet
from datetime import date, timedelta, datetime
from unittest.mock import patch, mock_open
import requests


# TEST FOR VIEWS
class SumsubViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.applicant_id = '12345'
        self.create_applicant_url = reverse('applicant-creation')
        # self.add_document_url = lambda pk: reverse('document-add', kwargs={'pk': pk})
        self.add_document_url = reverse('document-add', kwargs={'pk': self.applicant_id})
        self.get_verification_status_url = lambda pk: reverse('verification-status', kwargs={'pk': pk})
        self.get_saved_verification_data_url = lambda pk: reverse('saved-verification', kwargs={'pk': pk})
   
 
        self.applicant = VerificationStatus.objects.create(
            applicant_id='12345',
            country='USA',
            id_doc_type='passport',
            image_ids=['img1', 'img2'],
            image_review_results={'result': 'approved'},
            forbidden=False,
            partial_completion=False,
            step_statuses={'step1': 'completed', 'step2': 'pending'},
            image_statuses={'img1': 'approved', 'img2': 'pending'},
            selfie={'status': 'approved'},
        )

    # CREATE APPLICANT UNIT TEST
    @patch('requests.Session.send')
    def test_create_applicant_success(self, mock_send):
        """Test successfully creating an applicant"""
        
        # Mock the external API response
        mock_response = mock_send.return_value
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "id": "applicant-id-123",
            "externalUserId": "user-123",
            "status": "created"
        }

        # Prepare the request data
        data = {
            'externalUserId': 'user-123',
            'info': {'firstName': 'John', 'lastName': 'Doe'},
            'type': 'individual',
            'levelName': 'basic-kyc-level'
        }

        # Perform the request
        response = self.client.post(self.create_applicant_url, data, format='json')

        # Check that the mocked API call was made
        payload = {
            "externalUserId": 'user-123',
            "info": {'firstName': 'John', 'lastName': 'Doe'},
            "type": 'individual',
        }
        expected_url = 'https://api.sumsub.com/resources/applicants?levelName=basic-kyc-level'
        mock_send.assert_called_once()

        # Check response status and message
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('Applicant created successfully', response.data['message'])

    @patch('requests.Session.send')
    def test_create_applicant_missing_external_user_id(self, mock_send):
        """Test missing externalUserId returns a 400 error"""
        
        # Prepare the request data (missing externalUserId)
        data = {
            'info': {'firstName': 'John', 'lastName': 'Doe'},
            'type': 'individual',
            'levelName': 'basic-kyc-level'
        }

        # Perform the request
        response = self.client.post(self.create_applicant_url, data, format='json')

        # Check response status and message
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failed')
        self.assertIn('externalUserId is required', response.data['message'])

    @patch('requests.Session.send')
    def test_create_applicant_failed(self, mock_send):
        """Test failed applicant creation from Sumsub API"""
        
        # Mock the external API response for failure
        mock_response = mock_send.return_value
        mock_response.status_code = 400
        mock_response.json.return_value = {"error": "Invalid request"}

        # Prepare the request data
        data = {
            'externalUserId': 'user-123',
            'info': {'firstName': 'John', 'lastName': 'Doe'},
            'type': 'individual',
            'levelName': 'basic-kyc-level'
        }

        # Perform the request
        response = self.client.post(self.create_applicant_url, data, format='json')

        # Check response status and message for failure
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failed')

        # Since the error is returned in the 'error' field, check there
        self.assertIn('Invalid request', response.data['message']['error'])



    # ADD DOCUMENT UNIT TEST
    @patch('requests.get')
    @patch('requests.Session.send')
    def test_add_document_success(self, mock_send, mock_get):
        """Test successfully adding a document for the applicant"""
        
        # Mock the external image request response (requests.get)
        mock_get.return_value.status_code = 200
        mock_get.return_value.iter_content.return_value = [b'image data']

        # Mock the external Sumsub API response
        mock_response = mock_send.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {'message': 'Document added successfully'}

        data = {
            'img_url': 'https://example.com/img.jpg',
            'idDocType': 'passport',
            'country': 'US'
        }

        response = self.client.post(self.add_document_url, data, format='json')

        # Check that requests.get was called with the correct URL and timeout
        mock_get.assert_called_once_with('https://example.com/img.jpg', stream=True, timeout=10)
        
        # Check the response from the Sumsub API
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('Document added successfully', response.data['message'])

    def test_add_document_missing_fields(self):
        # Missing img_url, idDocType, or country
        data = {
            'img_url': 'http://example.com/img.jpg',  # Missing idDocType and country
        }

        response = self.client.post(self.add_document_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failed')
        self.assertEqual(response.data['message'], 'img_url, idDocType, and country are required')

    @patch('requests.get')
    def test_add_document_image_download_failed(self, mock_get):
        # Simulate a failure while downloading the image
        mock_get.side_effect = requests.exceptions.RequestException("Image download failed")

        data = {
            'img_url': 'http://example.com/img.jpg',
            'idDocType': 'passport',
            'country': 'USA',
        }

        response = self.client.post(self.add_document_url, data)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['status'], 'failed')
        self.assertEqual(response.data['message'], 'Image download failed')

    @patch('requests.Session.send')
    @patch('builtins.open', new_callable=mock_open, read_data=b'dummy image data')
    @patch('requests.get')
    def test_add_document_external_api_failure(self, mock_get, mock_open, mock_send):
        # Mock image download success
        mock_get.return_value.status_code = 200
        mock_get.return_value.iter_content = lambda chunk_size: [b'dummy image data']

        # Mock external API failure
        mock_send.return_value.status_code = 500
        mock_send.return_value.json.return_value = {"error": "API error"}

        data = {
            'img_url': 'http://example.com/img.jpg',
            'idDocType': 'passport',
            'country': 'USA',
        }

        response = self.client.post(self.add_document_url, data)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.data['status'], 'failed')
        self.assertEqual(response.data['message'], {'error': 'API error'})



    # GET APPLICANT VERIFICATION STATUS TEST
    @patch('requests.Session.send')
    def test_get_applicant_verification_status_success(self, mock_send):
        # Mock the response from the external API
        mock_response = {
            "IDENTITY": {
                "country": "USA",
                "idDocType": "passport",
                "imageIds": ["img1", "img2"],
                "imageReviewResults": {"result": "approved"},
                "forbidden": False,
                "partialCompletion": False,
                "stepStatuses": {"step1": "completed", "step2": "pending"},
                "imageStatuses": ["img1: approved", "img2: pending"],
            },
            "SELFIE": {"status": "approved"}
        }
        mock_send.return_value.status_code = 200
        mock_send.return_value.json.return_value = mock_response

        response = self.client.get(self.get_verification_status_url(self.id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)
        
        # Validate the data saved in the database
        verification_status = VerificationStatus.objects.get(applicant_id=self.id)
        self.assertEqual(verification_status.country, "USA")
        self.assertEqual(verification_status.id_doc_type, "passport")
        self.assertEqual(verification_status.image_ids, ["img1", "img2"])
        self.assertEqual(verification_status.image_review_results, {"result": "approved"})
        self.assertFalse(verification_status.forbidden)
        self.assertFalse(verification_status.partial_completion)
        self.assertEqual(verification_status.step_statuses, {"step1": "completed", "step2": "pending"})
        self.assertEqual(verification_status.image_statuses, ["img1: approved", "img2: pending"])
        self.assertEqual(verification_status.selfie, '{"status": "approved"}')

    @patch('requests.Session.send')
    def test_get_applicant_verification_status_api_error(self, mock_send):
        mock_send.return_value.status_code = 500  # Simulate a server error
        response = self.client.get(self.get_verification_status_url(self.id))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data['status'], 'failed')
        self.assertEqual(response.data['message'], 'Error fetching data from Sumsub.')


    # Saved verification status
    def test_get_saved_verification_data_success(self):
        response = self.client.get(self.get_saved_verification_data_url(self.applicant.applicant_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['applicant_id'], self.applicant.applicant_id)  

    def test_get_saved_verification_data_applicant_not_found(self):
        response = self.client.get(self.get_saved_verification_data_url('nonexistent_id'))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], 'failed')
        self.assertEqual(response.data['message'], 'Applicant not found')


# TEST FOR URLS
class SumsubURLTestCase(APITestCase):
    def test_create_applicant_url(self):
        url = reverse('applicant-creation')
        self.assertEqual(resolve(url).func.__name__, SumsubViewSet.as_view({'post': 'create_applicant'}).__name__)

    def test_add_document_url(self):
        url = reverse('document-add', kwargs={'pk': 'pk'})
        self.assertEqual(resolve(url).func.__name__, SumsubViewSet.as_view({'post': 'add_document'}).__name__)

    def test_view_book_url(self):
        url = reverse('verification-status', kwargs={'pk': 'pk'})
        self.assertEqual(resolve(url).func.__name__, SumsubViewSet.as_view({'get': 'get_applicant_verification_status'}).__name__)
    
    def test_filter_books_url(self):
        url = reverse('saved-verification', kwargs={'pk': 'pk'})
        self.assertEqual(resolve(url).func.__name__, SumsubViewSet.as_view({'get': 'get_saved_verification_data'}).__name__)



