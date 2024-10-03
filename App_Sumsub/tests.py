from django.urls import reverse, resolve
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.test import TestCase
from . models import *
from . views import SumsubViewSet
from datetime import date, timedelta, datetime
from unittest.mock import patch


# TEST FOR VIEWS
class SumsubViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.create_applicant_url = reverse('applicant-creation')
        self.add_document = lambda pk: reverse('document-add', kwargs={'pk': pk})
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

    def test_get_applicant_verification_status_missing_applicant_id(self):
        response = self.client.get(self.get_verification_status_url(None))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'failed')
        self.assertEqual(response.data['message'], 'Error fetching data from Sumsub.')

    @patch('requests.Session.send')
    def test_get_applicant_verification_status_api_error(self, mock_send):
        mock_send.return_value.status_code = 500  # Simulate a server error
        response = self.client.get(self.get_verification_status_url(self.id))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data['status'], 'failed')
        self.assertEqual(response.data['message'], 'Error fetching data from Sumsub.')

    def test_get_saved_verification_data_success(self):
        response = self.client.get(self.get_saved_verification_data_url(self.applicant.applicant_id))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['applicant_id'], self.applicant.applicant_id)  # Adjust field based on your serializer

    def test_get_saved_verification_data_missing_applicant_id(self):
        response = self.client.get(self.get_saved_verification_data_url(None))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], 'failed')
        self.assertEqual(response.data['message'], 'Applicant not found')

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



