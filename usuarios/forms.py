from django import forms
from .models import (Sala, AgendaConsulta, Consulta, Laudo, Receita, Atestado, Prontuario, 
                     Usuario, AgendaExame, AgendaTeleconsulta, Exame, Teleconsulta
)
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

#formulário para a criação de agenda de consulta
class AgendaConsultaForm(forms.ModelForm):
    class Meta:
        model = AgendaConsulta
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'horario_fim': forms.TimeInput(attrs={'type': 'time'}),
        }

#Formulário para a criação de agenda de exame
class AgendaExameForm(forms.ModelForm):
    class Meta:
        model = AgendaExame
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'horario_fim': forms.TimeInput(attrs={'type': 'time'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo_exame = cleaned_data.get('tipo_exame')
        sala = cleaned_data.get('sala')
        data = cleaned_data.get('data')
        horario_inicio = cleaned_data.get('horario_inicio')
        horario_fim = cleaned_data.get('horario_fim')
        duracao = cleaned_data.get('duracao_procedimento')

        if not tipo_exame:
            raise ValidationError("Tipo de exame é obrigatório.")

        if horario_inicio and horario_fim and horario_inicio >= horario_fim:
            raise ValidationError("O horário de início deve ser anterior ao horário de fim.")

        if duracao and duracao <= 0:
            raise ValidationError("A duração do exame deve ser maior que 0 minutos.")

        # Verifica conflitos de sala (pré-checagem simples)
        if sala and data and horario_inicio and horario_fim:
            conflitos_sala = AgendaExame.objects.filter(
                sala=sala,
                data=data,
                horario_inicio__lt=horario_fim,
                horario_fim__gt=horario_inicio
            ).exists()
            if conflitos_sala:
                raise ValidationError("Já existe exame marcado nessa sala e horário.")

        return cleaned_data

#form para agenda de teleconsulta
class AgendaTeleconsultaForm(forms.ModelForm):
    class Meta:
        model = AgendaTeleconsulta
        fields = '__all__'
        widgets = {
            'data': forms.DateInput(attrs={'type': 'date'}),
            'horario_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'horario_fim': forms.TimeInput(attrs={'type': 'time'}),
        }

#Form para agendamento de exame
class ExameForm(forms.ModelForm):
    class Meta:
        model = Exame
        fields = ['paciente', 'medico', 'tipo', 'agenda']
        widgets = {
            'agenda': forms.Select()
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Remove campo paciente se for um paciente logado
        if self.user and self.user.role == 'paciente':
            self.fields.pop('paciente')

        # IDs para AJAX
        self.fields['tipo'].widget.attrs.update({'id': 'id_tipo'})
        self.fields['agenda'].widget.attrs.update({'id': 'id_agenda'})

        # Corrigir erro ao validar: força preenchimento de queryset no POST
        tipo_exame = (
            self.data.get('tipo') or
            (self.instance and getattr(self.instance, 'tipo', None)) or
            (self.initial and self.initial.get('tipo'))
        )

        if tipo_exame:
            self.fields['agenda'].queryset = AgendaExame.objects.filter(
                tipo_exame=tipo_exame,
                status_manual='livre'
            ).order_by('data', 'horario_inicio')
        else:
            self.fields['agenda'].queryset = AgendaExame.objects.none()

    def clean(self):
        cleaned_data = super().clean()
        agenda = cleaned_data.get('agenda')
        paciente = cleaned_data.get('paciente') if 'paciente' in self.fields else self.initial.get('paciente')
        tipo = cleaned_data.get('tipo')
        medico = cleaned_data.get('medico')

        if not agenda:
            raise ValidationError("Selecione uma agenda válida.")

        if agenda.tipo_exame != tipo:
            raise ValidationError("A agenda selecionada não corresponde ao tipo de exame escolhido.")

        if not agenda.esta_disponivel:
            raise ValidationError("Este horário está indisponível para agendamento.")

        if paciente:
            conflito_paciente = Exame.objects.filter(
                paciente=paciente,
                agenda__data=agenda.data,
                agenda__horario_inicio=agenda.horario_inicio
            ).exclude(status='cancelada').exists()
            if conflito_paciente:
                raise ValidationError("Este paciente já possui um exame neste horário.")

        if medico:
            conflito_medico = Exame.objects.filter(
                medico=medico,
                agenda__data=agenda.data,
                agenda__horario_inicio=agenda.horario_inicio
            ).exclude(status='cancelada').exists()
            if conflito_medico:
                raise ValidationError("Este médico já está agendado neste horário.")

        return cleaned_data


#Formulário para o agendamento de consultas
from django.db.models import Q

class ConsultaForm(forms.ModelForm):
    class Meta:
        model = Consulta
        fields = ['paciente', 'medico', 'agenda']
        widgets = {
            'agenda': forms.Select()
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and user.role == 'paciente':
            self.fields.pop('paciente')

        # QuerySet inicial: agendas livres
        agendas_livres = AgendaConsulta.objects.filter(
            status_manual='livre'
        ).order_by('data', 'horario_inicio')

        # Exclui agendas com consulta ativa
        agendas_disponiveis = agendas_livres.exclude(
            consultas__status__in=['agendada', 'em_atendimento', 'finalizada']
        )

        self.fields['agenda'].queryset = agendas_disponiveis

    def clean(self):
        cleaned_data = super().clean()
        agenda = cleaned_data.get('agenda')
        paciente = cleaned_data.get('paciente') if 'paciente' in self.fields else self.initial.get('paciente')
        medico = cleaned_data.get('medico')

        if not agenda:
            raise ValidationError("Selecione um horário válido.")

        if not agenda.esta_disponivel:
            raise ValidationError("Este horário não está disponível para agendamento.")

        if agenda and medico and agenda.medico != medico:
            raise ValidationError("O médico selecionado não atende neste horário.")

        if paciente:
            conflito = Consulta.objects.filter(
                paciente=paciente,
                agenda__data=agenda.data,
                agenda__horario_inicio=agenda.horario_inicio
            ).exclude(status='cancelada').exists()
            if conflito:
                raise ValidationError("Você já possui uma consulta neste horário.")

        return cleaned_data

    
#Form para teleconsulta agendamento
class TeleconsultaForm(forms.ModelForm):
    class Meta:
        model = Teleconsulta
        fields = ['paciente', 'medico', 'agenda']
        widgets = {
            'agenda': forms.Select()
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Se for paciente, esconde o campo paciente
        if user and user.role == 'paciente':
            self.fields.pop('paciente')

        # Agendas livres
        agendas_livres = AgendaTeleconsulta.objects.filter(
            status_manual='livre'
        ).order_by('data', 'horario_inicio')

        # Exclui agendas que já possuem teleconsulta ativa
        agendas_disponiveis = agendas_livres.exclude(
            teleconsultas__status__in=['agendada', 'em_atendimento', 'finalizada']
        )

        self.fields['agenda'].queryset = agendas_disponiveis

    def clean(self):
        cleaned_data = super().clean()
        agenda = cleaned_data.get('agenda')
        paciente = cleaned_data.get('paciente') if 'paciente' in self.fields else self.initial.get('paciente')
        medico = cleaned_data.get('medico')

        if not agenda:
            raise ValidationError("Selecione um horário válido.")

        if not agenda.esta_disponivel:
            raise ValidationError("Este horário não está disponível para agendamento.")

        if agenda and medico and agenda.medico != medico:
            raise ValidationError("O médico selecionado não atende neste horário.")

        if paciente:
            conflito = Teleconsulta.objects.filter(
                paciente=paciente,
                agenda__data=agenda.data,
                agenda__horario_inicio=agenda.horario_inicio
            ).exclude(status='cancelada').exists()
            if conflito:
                raise ValidationError("Você já possui uma teleconsulta neste horário.")

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

