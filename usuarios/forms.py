from django import forms
from .models import Sala, Agenda, Consulta
from django.core.exceptions import ValidationError
from django.utils import timezone

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
    
#Formulário para o agendamento de consultas
class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['paciente', 'medico', 'agenda']  # paciente pode ser ocultado via lógica na view
        widgets = {
            'agenda': forms.Select()
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # pegamos o user da view
        super().__init__(*args, **kwargs)

        # Se for paciente, escondemos o campo 'paciente'
        if user and user.role == 'paciente':
            self.fields.pop('paciente')

        # Filtrar agendas disponíveis (do tipo consulta e ativas e sem consulta associada)
        self.fields['agenda'].queryset = Agenda.objects.filter(
            procedimento='consulta',
            ativo=True
        ).exclude(consulta__isnull=False).order_by('data', 'horario_inicio')

    def clean(self):
        cleaned_data = super().clean()
        agenda = cleaned_data.get('agenda')
        paciente = cleaned_data.get('paciente') if 'paciente' in cleaned_data else self.initial.get('paciente')
        medico = cleaned_data.get('medico')

        # Verifica se a agenda já está ocupada (segurança extra)
        if Consulta.objects.filter(agenda=agenda).exists():
            raise ValidationError("Este horário já está agendado.")

        # Valida se o médico da consulta é o mesmo da agenda
        if agenda and medico and agenda.medico != medico:
            raise ValidationError("O médico selecionado não corresponde ao da agenda.")

        # Verifica se o paciente já tem atendimento no mesmo horário
        if paciente and agenda:
            conflito = Consulta.objects.filter(
                paciente=paciente,
                agenda__data=agenda.data,
                agenda__horario_inicio=agenda.horario_inicio
            ).exists()
            if conflito:
                raise ValidationError("Este paciente já tem uma consulta ou exame neste horário.")

        return cleaned_data