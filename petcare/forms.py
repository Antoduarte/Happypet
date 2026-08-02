# forms.py
from django import forms
from .models import Owner, Pet, MedicalRecord, MedicalAttachment

class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = '__all__'
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
        

class PetForm(forms.ModelForm):
    class Meta:
        model = Pet
        fields = '__all__'
        widgets = {
            'owner': forms.Select(attrs={'class': 'form-select  form-select-sm'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'species': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'breed': forms.TextInput(attrs={'class': 'form-control'}),
            'gender': forms.Select(attrs={'class': 'form-select form-select-sm'}),
            'color': forms.TextInput(attrs={'class': 'form-control'}),
            'age': forms.NumberInput(attrs={'class': 'form-control'}),
            'microchip': forms.TextInput(attrs={'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'special_notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        exclude = ['pet'] 
        fields = '__all__'
        widgets = {
            'visit_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'next_checkup': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'visit_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 2 }),
            'visit_motive': forms.Textarea(attrs={'class': 'form-control', 'rows': 2 }),
            'temperament': forms.Select(attrs={'class': 'form-control'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4 }),
            'treatment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4 }),
            'prescribed_meds': forms.Textarea(attrs={'class': 'form-control', 'rows': 4 }),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control'}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'respiratory_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'veterinarian': forms.TextInput(attrs={'class': 'form-control'}),
   
        }


class AttachmentForm(forms.ModelForm):
    class Meta:
        model = MedicalAttachment
        fields = ['file', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Descripción del archivo', 'class': 'form-control form-control-sm'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
        valid_extensions = [
            'pdf', 'doc', 'docx', 'xls', 'xlsx', 
            'jpg', 'jpeg', 'png', 'txt', 'csv'
        ]
        
        self.fields['file'].widget.attrs.update({
            'accept': ', '.join(f'.{ext}' for ext in valid_extensions),
            'class': 'form-control form-control-sm'
        })
