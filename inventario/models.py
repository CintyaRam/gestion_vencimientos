from django.db import models
from django.contrib.auth.models import User
from datetime import date

class Departamento(models.Model):
    numero_departamento = models.CharField(max_length=3, primary_key=True)

    def __str__(self):
        return f"Departamento {self.numero_departamento}"
    
class Articulo(models.Model):
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.nombre
    
    def lotes_activos(self):
        return self.lotes.filter(activo=True)
    
class Lote(models.Model):
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE, related_name='lotes')
    numero_lote = models.CharField(max_length=100)
    fecha_vencimiento = models.DateField()
    responsable_registro = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lotes_registrados')
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Lote {self.numero_lote} de {self.articulo.nombre}"
    
    def estado_vencimiento(self):
        hoy = date.today()
        dias_restantes = (self.fecha_vencimiento - hoy).days
    
        if dias_restantes <= 0:
            return 'Vencido - Quitar de Sala inmediatamente'
        elif dias_restantes <= 2:
            return 'Por vencer (tomar acción correctiva)'
        elif dias_restantes <= 7:
            return 'Cerca de vencimiento'
        else:
            return 'Buen estado'