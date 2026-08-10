# forms.py
from django import forms
from .models import Owner, Pet, MedicalRecord, MedicalAttachment

class OwnerForm(forms.ModelForm):
    class Meta:
        model = Owner
        fields = ['first_name', 'last_name', 'phone', 'address', 'id_number']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'id_number': forms.TextInput(attrs={'class': 'form-control'}),
        }
        

class PetForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['owner'].empty_label = 'Seleccione un dueño'

    class Meta:
        model = Pet
        fields = [
            'owner', 'name', 'species', 'breed', 'gender',
            'color', 'microchip', 'age', 'allergies', 'special_notes'
        ]
        widgets = {
            'owner': forms.Select(attrs={'class': 'form-select form-select-sm select2-searchable', 'data-select2-modal': '#addPet'}),
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['treatment'].help_text = (
            'Escriba un tratamiento por línea para que se impriman separados.'
        )

    class Meta:
        model = MedicalRecord
        exclude = ['pet']
        widgets = {
            'visit_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'next_checkup': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'visit_reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 2 }),
            'visit_motive': forms.Textarea(attrs={'class': 'form-control', 'rows': 2 }),
            'temperament': forms.Select(attrs={'class': 'form-control'}),
            'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4 }),
            'treatment': forms.Textarea(attrs={'class': 'form-control', 'rows': 5 }),
            'prescribed_meds': forms.Textarea(attrs={'class': 'form-control', 'rows': 4 }),
            'weight': forms.NumberInput(attrs={'class': 'form-control'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control'}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'respiratory_rate': forms.NumberInput(attrs={'class': 'form-control'}),
            'veterinarian': forms.TextInput(attrs={'class': 'form-control'}),

        }


class AttachmentForm(forms.ModelForm):
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
    VALID_EXTENSIONS = {
        'pdf', 'doc', 'docx', 'xls', 'xlsx',
        'jpg', 'jpeg', 'png', 'txt', 'csv'
    }

    class Meta:
        model = MedicalAttachment
        fields = ['file', 'description']
        widgets = {
            'description': forms.TextInput(attrs={'placeholder': 'Descripción del archivo', 'class': 'form-control form-control-sm'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['file'].widget.attrs.update({
            'accept': ', '.join(f'.{ext}' for ext in sorted(self.VALID_EXTENSIONS)),
            'class': 'form-control form-control-sm'
        })

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if not file:
            return file

        extension = file.name.lower().split('.')[-1]
        if extension not in self.VALID_EXTENSIONS:
            raise forms.ValidationError(
                f'Formato no permitido. Extensiones válidas: {", ".join(sorted(self.VALID_EXTENSIONS))}'
            )

        if file.size > self.MAX_FILE_SIZE:
            raise forms.ValidationError(
                f'El archivo no puede superar los {self.MAX_FILE_SIZE // (1024 * 1024)} MB.'
            )

        return file
