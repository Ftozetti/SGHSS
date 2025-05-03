from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.conf import settings




#Model para a criação de usuarios e perfis
class Usuario(AbstractUser):
    # Tipos de perfil
    ROLE_CHOICES = [
        ('paciente', 'Paciente'),
        ('medico', 'Médico'),
        ('administrativo', 'Administrativo'),
        ('financeiro', 'Financeiro'),
    ]

    # Campos comuns
    cpf = models.CharField(max_length=14, unique=True, blank=False, null=False)
    telefone = models.CharField(max_length=20)
    rua = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    bairro = models.CharField(max_length=50)
    cidade = models.CharField(max_length=50)
    estado = models.CharField(max_length=2)
    cep = models.CharField(max_length=9)

    # Perfil
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    # Campos específicos por perfil
    # Paciente
    plano_saude = models.CharField(max_length=50, null=True, blank=True)
    numero_cartao_plano = models.CharField(max_length=30, null=True, blank=True)

    # Médico
    crm = models.CharField(max_length=20, null=True, blank=True)
    especialidade = models.CharField(max_length=50, null=True, blank=True)

    # Administrativo e Financeiro
    setor = models.CharField(max_length=50, null=True, blank=True)
    cargo = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def tipo_usuario(self):
        return dict(self.ROLE_CHOICES).get(self.role, 'Usuário')
    
#Modelo para a criação e edição de salas e controle da estrutura fisica
class Sala(models.Model):
    TIPO_CHOICES = [
        ('consulta', 'Consulta'),
        ('exame', 'Exame'),
    ]

    numero = models.CharField("Número da Sala", max_length=10, unique=True)
    tipo = models.CharField("Tipo", max_length=10, choices=TIPO_CHOICES)
    equipamentos = models.TextField("Equipamentos Instalados", blank=True, null=True)
    observacoes = models.TextField("Observações", blank=True, null=True)

    def __str__(self):
        return f"Sala {self.numero} - {self.get_tipo_display()}"
    
#Modelo para a criação de agenda médica    
class Agenda(models.Model):
    PROCEDIMENTO_CHOICES = [
        ('consulta', 'Consulta'),
        ('exame', 'Exame'),
    ]

    EXAME_CHOICES = [
        ('radiografia', 'Radiografia'),
        ('ultrassonografia', 'Ultrassonografia'),
        ('tomografia', 'Tomografia Computadorizada'),
        ('mamografia', 'Mamografia'),
        ('doppler', 'Doppler'),
    ]

    procedimento = models.CharField(max_length=20, choices=PROCEDIMENTO_CHOICES)
    tipo_exame = models.CharField(max_length=30, choices=EXAME_CHOICES, blank=True, null=True)
    medico = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'medico'})
    sala = models.ForeignKey(Sala, on_delete=models.PROTECT)
    data = models.DateField()
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    duracao_procedimento = models.PositiveIntegerField(help_text="Duração em minutos")
    ativo = models.BooleanField(default=True)  # se foi excluído ou não

    def __str__(self):
        return f"{self.get_procedimento_display()} - {self.data} - {self.horario_inicio} às {self.horario_fim} ({self.sala})"
    
    def clean(self):
        if self.procedimento == 'consulta' and self.tipo_exame:
            raise ValidationError("Tipo de exame deve estar vazio para consultas.")
        if self.procedimento == 'exame' and not self.tipo_exame:
            raise ValidationError("Tipo de exame é obrigatório para exames.")

    def save(self, *args, **kwargs):
        self.full_clean()  # chama o método clean antes de salvar
        super().save(*args, **kwargs)

    @property
    def status(self):
        from usuarios.models import Consulta  # importação local evita erro de import circular

        if self.procedimento == 'consulta' and Consulta.objects.filter(agenda=self).exists():
            return "Agendado"
    
        return "Livre"
    
#Classe abstrata para reaproveitas informações para exames, consultas e teleconsultas
class AtendimentoBase(models.Model):
    STATUS_CHOICES = [
        ('agendada', 'Agendada'),
        ('cancelada', 'Cancelada'),
        ('em_andamento', 'Em atendimento'),
        ('finalizada', 'Finalizada'),
    ]

    agenda = models.OneToOneField(Agenda, on_delete=models.PROTECT)
    medico = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    limit_choices_to={'role': 'medico'},
    related_name='consultas_como_medico'
)
    paciente = models.ForeignKey(
    settings.AUTH_USER_MODEL,
    on_delete=models.CASCADE,
    limit_choices_to={'role': 'paciente'},
    related_name='consultas_como_paciente'
)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='agendada')
    observacoes_visiveis = models.TextField(blank=True, null=True)
    observacoes_internas = models.TextField(blank=True, null=True)
    encaminhamento = models.TextField(blank=True, null=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

#Classe Consulta    
class Consulta(AtendimentoBase):
    cancelado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultas_canceladas'
    )
    motivo_cancelamento = models.TextField(blank=True, null=True)
    valor = models.DecimalField(max_digits=8, decimal_places=2, default=250.00)

    def __str__(self):
        return f"Consulta de {self.paciente.get_full_name()} com {self.medico.get_full_name()} em {self.agenda.data} às {self.agenda.horario_inicio}"