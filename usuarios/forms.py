from django import forms
from .models import Sala, Agenda
from django.core.exceptions import ValidationError

#formulário para a criação de salas e estrutura fisica
class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['numero', 'tipo', 'equipamentos', 'observacoes']
        widgets = {
            'equipamentos': forms.Textarea(attrs={'rows': 2}),
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }

#formulário para a criação de agenda
class AgendaForm(forms.ModelForm):
    class Meta:
        model = Agenda
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'horario_fim': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        procedimento = cleaned_data.get('procedimento')
        tipo_exame = cleaned_data.get('tipo_exame')

        if procedimento == 'consulta' and tipo_exame:
            raise ValidationError("Tipo de exame deve estar vazio para consultas.")

        if procedimento == 'exame' and not tipo_exame:
            raise ValidationError("Tipo de exame é obrigatório para exames.")

        return cleaned_data