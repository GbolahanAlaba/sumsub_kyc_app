from django.urls import reverse, resolve
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from django.test import TestCase
from . models import *
from . views import SumsubViewSet
from datetime import date, timedelta, datetime


# TEST FOR VIEWS
class SumsubViewSetTestCase(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.enroll_user_url = reverse('user-enroll')
        self.books_url = reverse('all-books')
        self.view_book_url = lambda book_id: reverse('book-view', kwargs={'book_id': book_id})
        self.borrow_book_url = reverse('book-borrow')
        self.add_book_url = reverse('book-add')
        self.remove_book_url = lambda book_id: reverse('book-remove', kwargs={'book_id': book_id})
 
        



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



