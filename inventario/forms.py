from django import forms
from .models import Articulo, Lote

class ArticuloForm(forms.ModelForm):
    class Meta:
        model = Articulo
        fields = '__all__'


class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        exclude = ['responsable_registro', 'activo']  # ⬅️ Ocultamos ambos
        widgets = {
            'fecha_vencimiento': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")