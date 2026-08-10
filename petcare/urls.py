from django.urls import path
from .views import CreateOwnerView, CreatePetView, OwnerListView, PetDetailView, OwnerDetailView, EditOwnerView, EditPetView, \
                   CreateMedicalRecordView, DeleteOwnerView, DeletePetView, MedicalRecordDetailView, MedicalRecordUpdateView, \
                   MedicalRecordDeleteView, delete_attachment, print_medical_record
from django.views.generic import TemplateView

urlpatterns = [
    path('', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
    path('pet-owner/', OwnerListView.as_view(), name='pet_list'),
    path('pet/detail/<int:pk>', PetDetailView.as_view(), name='pet_detail'),
    path('owner/detail/<int:pk>', OwnerDetailView.as_view(), name='owner_detail'),

    path('pets/new', CreatePetView.as_view(), name='create_pet'),
    path('pets/<int:pk>/edit/', EditPetView.as_view(), name='edit_pet'),
    path('pets/<int:pk>/delete/', DeletePetView.as_view(), name='delete_pet'),

    path('owners/<int:pk>/delete/', DeleteOwnerView.as_view(), name='delete_owner'),
    path('owners/new', CreateOwnerView.as_view(), name='create_owner'),
    path('owners/<int:pk>/edit/', EditOwnerView.as_view(), name='edit_owner'),

    path('pet/<int:pk>/record/new', CreateMedicalRecordView.as_view(), name='create_pet_medical_record'),
    path('records/<int:pk>/', MedicalRecordDetailView.as_view(), name='medical_record_detail'),
    path('records/<int:pk>/edit/', MedicalRecordUpdateView.as_view(), name='edit_medical_record'),
    path('records/<int:pk>/delete/', MedicalRecordDeleteView.as_view(), name='delete_medical_record'),
    path('records/<int:pk>/print/', print_medical_record, name='print_medical_record'),

    path('attachments/<int:pk>/delete/', delete_attachment, name='delete_attachment'),
]
