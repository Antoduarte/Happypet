from django.urls import path, re_path
from .views import CreateOwnerView, CreatePetView, OwnerListView, PetDetailView, OwnerDetailView, EditOwnerView, EditPetView, \
                   CreateMedicalRecordView, DeleteOwnerView, DeletePetView, MedicalRecordDetailView, MedicalRecordUpdateView, \
                   MedicalRecordDeleteView, delete_attachment, print_medical_record

urlpatterns = [
    re_path(r'^pet-owner/$', OwnerListView.as_view(), name='pet_list'),
    re_path(r'^pet/detail/(?P<pk>\d+)$', PetDetailView.as_view(), name='pet_detail'),
    re_path(r'^owner/detail/(?P<pk>\d+)$', OwnerDetailView.as_view(), name='owner_detail'),


    re_path(r'^pets/new$', CreatePetView.as_view(), name='create_pet'),
    re_path(r'^pets/(?P<pk>\d+)/edit/$', EditPetView.as_view(), name='edit_pet'),
    re_path(r'^pets/(?P<pk>\d+)/delete/$', DeletePetView.as_view(), name='delete_pet'),
    
    
    re_path(r'^owners/(?P<pk>\d+)/delete/$', DeleteOwnerView.as_view(), name='delete_owner'),
    re_path(r'^owners/new$', CreateOwnerView.as_view(), name='create_owner'),
    re_path(r'^owners/(?P<pk>\d+)/edit/$', EditOwnerView.as_view(), name='edit_owner'),
    
    re_path(r'^pet/(?P<pk>\d+)/record/new$', CreateMedicalRecordView.as_view(), name='create_pet_medical_record'),
    re_path(r'^records/(?P<pk>\d+)/$', MedicalRecordDetailView.as_view(), name='medical_record_detail'),
    re_path(r'^records/(?P<pk>\d+)/edit/$', MedicalRecordUpdateView.as_view(), name='edit_medical_record'),
    re_path(r'^records/(?P<pk>\d+)/delete/$', MedicalRecordDeleteView.as_view(), name='delete_medical_record'),
    re_path(r'^records/(?P<pk>\d+)/print/$', print_medical_record, name='print_medical_record'),
    
    re_path(r'^attachments/(?P<pk>\d+)/delete/$', delete_attachment, name='delete_attachment'),
]
