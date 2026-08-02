
from django.db import models

class Owner(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, unique=True)
    address = models.CharField(max_length=200)
    id_number = models.CharField(max_length=20, unique=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Pet(models.Model):
    SPECIES_CHOICES = [
        ('PERRO', 'Canino'),
        ('GATO', 'Felino'),
        ('AVE', 'Ave'),
        ('ROEDOR', 'Roedor'),
        ('BOVINO', 'Bovino'),
        ('EQUINO', 'Equino'),
        ('OTRO', 'Especie no especificada'),
    ]
    
    GENDER_CHOICES = [('M', 'Macho'), ('H', 'Hembra')]
    
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE, related_name='pets')
    name = models.CharField(max_length=100)
    species = models.CharField(max_length=20, choices=SPECIES_CHOICES)
    breed = models.CharField(max_length=50)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    color = models.CharField(max_length=50)
    microchip = models.CharField(max_length=100, unique=True, null=True, blank=True)
    age = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    allergies = models.TextField(blank=True)
    special_notes = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_species_display()})"

class MedicalRecord(models.Model):
    
    TEMPERAMENT_CHOICES = [
        ('DOCIL', 'Dócil'),
        ('JUGUETON', 'Juguetón'),
        ('NERVIOSO', 'Nervioso'),
        ('AGRESIVO', 'Agresivo'),
    ]
    
    pet = models.ForeignKey(Pet, on_delete=models.CASCADE, related_name='medical_records', null=True, blank=True)
    visit_date = models.DateTimeField()
    visit_reason = models.CharField(max_length=200)
    visit_motive = models.CharField(max_length=300, null=True, blank=True, help_text="Motivo de la visita")
    diagnosis = models.TextField()
    treatment = models.TextField()
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    heart_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Frecuencia cardiaca en bpm")
    respiratory_rate = models.PositiveIntegerField(null=True, blank=True, help_text="Frecuencia respiratoria en rpm")
    veterinarian = models.CharField(max_length=100)
    prescribed_meds = models.TextField(blank=True)
    next_checkup = models.DateField(null=True, blank=True)
    temperament = models.CharField(
        max_length=50,
        choices=TEMPERAMENT_CHOICES,
        null=True,
        blank=True,
        help_text="Comportamiento o temperamento de la mascota durante el diagnóstico"
    )
    
    class Meta:
        verbose_name_plural = "Historiales Médicos"
    
    def __str__(self):
        return f"Historial de {self.mascota} - {self.fecha_visita.date()}"

class MedicalAttachment(models.Model):
    record = models.ForeignKey(MedicalRecord, on_delete=models.CASCADE, related_name='medical_attachments')
    file = models.FileField(upload_to='medical_records/attachments/%Y/%m/%d/')
    description = models.CharField(max_length=255, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.description or 'Sin descripción'} - {self.file.name}"
