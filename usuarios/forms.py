from django import forms
from .models import Sala, Agenda, Consulta, Laudo, Receita, Atestado, Prontuario, Usuario
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q

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
            ativo=True,
            status_manual='livre'
        ).exclude(
            consultas__status='agendada'
        ).order_by('data', 'horario_inicio')

    def clean(self):
        cleaned_data = super().clean()
        agenda = cleaned_data.get('agenda')
        paciente = cleaned_data.get('paciente') if 'paciente' in cleaned_data else self.initial.get('paciente')
        medico = cleaned_data.get('medico')

        # Verifica se a agenda já está ocupada (segurança extra)
        if agenda.consultas.filter(status='agendada').exists():
            raise ValidationError("Este horário já está agendado.")

        # Valida se o médico da consulta é o mesmo da agenda
        if agenda and medico and agenda.medico != medico:
            raise ValidationError("O médico selecionado não corresponde ao da agenda.")

        # Verifica se o paciente já tem atendimento no mesmo horário
        if paciente and agenda:
            conflito = Consulta.objects.filter(
            paciente=paciente,
            agenda__data=agenda.data,
            agenda__horario_inicio=agenda.horario_inicio,
            status='agendada'
        ).exists()
            if conflito:
                raise ValidationError("Este paciente já tem uma consulta ou exame neste horário.")

        return cleaned_data

#Form para efetuar o cancelamento da consulta    
class CancelamentoConsultaForm(forms.Form):
    motivo_cancelamento = forms.CharField(
        label='Motivo do cancelamento (opcional)',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
    liberar_horario = forms.BooleanField(
        label='Deseja liberar o horário para que outro paciente possa agendar?',
        required=False,
        initial=True
    )

#Form para a criação de documentos medicos em consultas
class LaudoForm(forms.ModelForm):
    class Meta:
        model = Laudo
        fields = ['conteudo']

class ReceitaForm(forms.ModelForm):
    class Meta:
        model = Receita
        fields = ['conteudo']

class AtestadoForm(forms.ModelForm):
    class Meta:
        model = Atestado
        fields = ['conteudo']

#Formulário para o preenchimento do prontuário
class ProntuarioForm(forms.ModelForm):
    class Meta:
        model = Prontuario
        fields = ['alergias', 'tratamentos', 'historico_cirurgias', 'observacoes_medicas']

#Form para capturar as informações de observações em consultas
class ObservacoesConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['observacoes_visiveis', 'observacoes_internas']
        widgets = {
            'observacoes_visiveis': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'observacoes_internas': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

#Forms para selecionar paciente
class SelecionarPacienteForm(forms.Form):
    paciente = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(role='paciente', is_active=True),
        label="Selecione um paciente",
        widget=forms.Select(attrs={'class': 'form-control'})
    )