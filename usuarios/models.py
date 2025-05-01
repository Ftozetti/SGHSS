from django.db import models
from django.contrib.auth.models import AbstractUser


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
