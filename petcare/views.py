# views.py
from django.views.generic import CreateView, ListView, UpdateView, DetailView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from django.contrib import messages
from django.urls import reverse_lazy
from .forms import OwnerForm, PetForm, MedicalRecordForm, AttachmentForm
from .models import Owner, Pet, MedicalRecord, MedicalAttachment
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.db.models import Q
from django.shortcuts import redirect, get_object_or_404
import pdfkit
# from xhtml2pdf import pisa



""" Create Views"""
class CreateOwnerView(LoginRequiredMixin, CreateView):
    model = Owner
    form_class = OwnerForm
    template_name = 'pets_owners.html'
    success_url = reverse_lazy('pet_list')
    
    def form_invalid(self, form):
        """Maneja los errores de validación del formulario"""
        field_name = {
            'phone': 'Numero de Telefono',
            'id_number': 'Identificador'
        }
        
        for field, errors in form.errors.items():
            if 'already exists' in str(errors):
                field_label = field_name[field]
                messages.error(
                    self.request,
                    f'Error: {field_label} ya existe en el sistema. Por favor use otro.'
                )
                break
        else:
            messages.error(
                self.request,
                'Por favor corrija los errores en el formulario.'
            )
        
        return redirect('pet_list')

    def form_valid(self, form):
        messages.success(
            self.request,
            '¡Nuevo dueño registrado exitosamente!'
        )
        return super().form_valid(form)

class CreatePetView(LoginRequiredMixin, CreateView):
    model = Pet
    form_class = PetForm
    template_name = 'pets_owners.html'
    success_url = reverse_lazy('pet_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owners'] = Owner.objects.all()
        return context
    
    def form_valid(self, form):
            messages.success(
                self.request,
                '¡Nueva Mascota registrada exitosamente!'
            )
            return super().form_valid(form)

class CreateMedicalRecordView(LoginRequiredMixin, CreateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'pet_owner_detail.html'

    def form_valid(self, form):
        form.instance.pet = Pet.objects.get(pk=self.kwargs['pk'])
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('pet_detail', kwargs={'pk': self.kwargs['pk']})


""" List Views"""
class OwnerListView(LoginRequiredMixin, ListView):
    model = Owner
    template_name = 'pets_owners.html'
    context_object_name = 'owners' 
    paginate_by = 15
    ordering = ['-registration_date']
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner_form'] = OwnerForm()
        context['pet_form'] = PetForm()
        context['search_query'] = self.request.GET.get('q', '')
        return context

    def get_queryset(self):
        queryset = super().get_queryset().prefetch_related('pets')
        search_query = self.request.GET.get('q')
        
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(id_number__icontains=search_query) |
                Q(phone__icontains=search_query) |
                Q(pets__name__icontains=search_query)
            )
        return queryset
    
""" Detail Views"""
class PetDetailView(LoginRequiredMixin, DetailView):
    model = Pet
    template_name = 'pet_owner_detail.html'
    context_object_name = 'pet'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pet_form'] = PetForm(instance=self.object)
        context['medical_record_form'] = MedicalRecordForm()
        return context

    def get_queryset(self):
        return Pet.objects.select_related('owner').prefetch_related('medical_records')
    
class OwnerDetailView(LoginRequiredMixin, DetailView):
    model = Owner
    template_name = 'owner_detail.html'
    context_object_name = 'owner'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['owner_form'] = OwnerForm(instance=self.object)
        return context
    
class MedicalRecordDetailView(LoginRequiredMixin, DetailView):
    model = MedicalRecord
    template_name = 'pet_medical_record_detail.html'
    context_object_name = 'record'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pet'] = self.object.pet
        context['attachment_form'] = AttachmentForm()
        context['attachments'] = self.object.medical_attachments.all()
        context['medical_record_form'] = MedicalRecordForm(instance=self.object)
        return context


""" Edit Views"""
class EditOwnerView(LoginRequiredMixin, UpdateView):
    model = Owner
    form_class = OwnerForm
    template_name = 'pet_owner_detail.html'

    def get_success_url(self):
        return reverse_lazy('owner_detail', kwargs={'pk': self.kwargs['pk']})
    
    def form_invalid(self, form):
        """Maneja los errores de validación del formulario"""
        field_name = {
            'phone': 'Numero de Telefono',
            'id_number': 'Identificador'
        }
        
        for field, errors in form.errors.items():
            if 'already exists' in str(errors):
                field_label = field_name[field]
                messages.error(
                    self.request,
                    f'Error: {field_label} ya existe en el sistema. Por favor use otro.'
                )
                break
        else:
            messages.error(
                self.request,
                'Por favor corrija los errores en el formulario.'
            )
        
        return redirect(self.get_success_url())
    
    def form_valid(self, form):
        messages.success(
            self.request,
            '¡Dueño Actualizado exitosamente!'
        )
        return super().form_valid(form)


class EditPetView(LoginRequiredMixin, UpdateView):
    model = Pet
    form_class = PetForm
    template_name = 'pet_detail.html'

    def get_success_url(self):
        return reverse_lazy('pet_detail', kwargs={'pk': self.kwargs['pk']})
    
class MedicalRecordUpdateView(LoginRequiredMixin, UpdateView):
    model = MedicalRecord
    form_class = MedicalRecordForm
    template_name = 'pet_medical_record_detail.html'
    
    def form_valid(self, form):
        if self.object.pet:
            form.instance.pet = self.object.pet
        return super().form_valid(form)
    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        attachment_form = AttachmentForm(request.POST, request.FILES)

        if 'submit_attachment' in request.POST and attachment_form.is_valid():
            attachment = attachment_form.save(commit=False)
            attachment.record = self.object
            attachment.save()
            return redirect(self.get_success_url())
        else:
            return self.form_valid(form)

    def get_success_url(self):
        return reverse_lazy('medical_record_detail', kwargs={'pk': self.kwargs['pk']})

""" Delete Views"""
class DeleteOwnerView(LoginRequiredMixin, DeleteView):
    model = Owner
    template_name = 'pet_owner_detail.html'
    success_url = reverse_lazy('pet_list')

    
class DeletePetView(LoginRequiredMixin, DeleteView):
    model = Pet
    template_name = 'pet_owner_detail.html'
    success_url = reverse_lazy('pet_list')

class MedicalRecordDeleteView(LoginRequiredMixin, DeleteView):
    model = MedicalRecord
    template_name = 'pet_medical_record_detail.html'
    
    def get_success_url(self):
        pet_id = self.object.pet.id
        return reverse_lazy('pet_detail', kwargs={'pk': pet_id})
    

@login_required()
def delete_attachment(request, pk):
    attachment = get_object_or_404(MedicalAttachment, pk=pk)
    record_pk = attachment.record.pk
    
    file = attachment.file
    if file:
        try:
            file.delete(save=False) 
        except:
            pass
        
    attachment.delete()
    return redirect('medical_record_detail', pk=record_pk)


@login_required()
def print_medical_record(request, pk):
    record = MedicalRecord.objects.get(pk=pk)
    html = render_to_string('medical_records/ticket.html', {'record': record})
    config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')
    options = {
        'page-width': '80mm',
        'page-height': '200mm',
        'margin-top': '5mm',
        'margin-right': '5mm',
        'margin-bottom': '5mm',
        'margin-left': '5mm',
        'encoding': "UTF-8",
        'no-outline': None,
    }
    pdf = pdfkit.from_string(html, False, options=options, configuration=config)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="ticket_{record.id}.pdf"'
    return response

# def print_medical_record(request, pk):
#     record = MedicalRecord.objects.get(pk=pk)
#     html = render_to_string('medical_records/ticket.html', {'record': record})
    
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'filename="ticket_{record.id}.pdf"'
    
#     pisa_status = pisa.CreatePDF(html, dest=response)
#     if pisa_status.err:
#         return HttpResponse('Error al generar PDF')
#     return response
