from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter
from . views import *



urlpatterns = [
   path('create-applicant/', SumsubViewSet.as_view({'post': 'create_applicant'}), name='applicant-creation'),
   path('add-id-document/<str:pk>/', SumsubViewSet.as_view({'post': 'add_document'}), name='document-add'),
   path('fetch-verification-status/<str:pk>/', SumsubViewSet.as_view({'get': 'fetch_verification_status'}), name='verification-status-fetch'),
   path('all-saved-verification-status/', SumsubViewSet.as_view({'get': 'fetch_all_saved_verification_data'}), name='all_saved-verification-fetch'),
   path('get-saved-verification-status/<str:pk>/', SumsubViewSet.as_view({'get': 'get_saved_verification_data'}), name='saved-verification'),
]