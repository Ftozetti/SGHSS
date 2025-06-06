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
class AgendaBase(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.PROTECT)
    data = models.DateField()
    horario_inicio = models.TimeField()
    horario_fim = models.TimeField()
    duracao_procedimento = models.PositiveIntegerField(help_text="Duração em minutos")
    status_manual = models.CharField(
        max_length=20,
        choices=[('livre', 'Livre'), ('agendado', 'Agendado'), ('bloqueado', 'Bloqueado')],
        default='livre'
    )

    class Meta:
        abstract = True

    def clean(self):
        conflitos = type(self).objects.filter(
            sala=self.sala,
            data=self.data,
            horario_inicio__lt=self.horario_fim,
            horario_fim__gt=self.horario_inicio,
        ).exclude(pk=self.pk)

        if conflitos.exists():
            raise ValidationError("Essa sala já está ocupada nesse horário.")

    @property
    def esta_disponivel(self):
        return self.status_manual != 'bloqueado' and not self.tem_procedimento_ativo()

    def tem_procedimento_ativo(self):
        raise NotImplementedError("Subclasses devem implementar essa verificação.")
    
#Agenda Consultas    
class AgendaConsulta(AgendaBase):
    medico = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=False, limit_choices_to={'role': 'medico'})

    def tem_procedimento_ativo(self):
        return self.consultas.exclude(status='cancelada').exists()
    
    def __str__(self):
        return f"{self.medico.get_full_name()} - {self.data.strftime('%d/%m/%Y')} às {self.horario_inicio.strftime('%H:%M')}"


#Criação da Agenda de Exames
class AgendaExame(AgendaBase):
    EXAME_CHOICES = [
        ('radiografia', 'Radiografia'),
        ('ultrassonografia', 'Ultrassonografia'),
        ('tomografia', 'Tomografia Computadorizada'),
        ('mamografia', 'Mamografia'),
        ('doppler', 'Doppler'),
    ]

    tipo_exame = models.CharField(max_length=30, choices=EXAME_CHOICES)
    medico = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=True, limit_choices_to={'role': 'medico'})

    def tem_procedimento_ativo(self):
        return self.exames.exclude(status='cancelada').exists()
    
    def __str__(self):
        return f"{self.get_tipo_exame_display()} - Sala {self.sala.numero} - {self.data.strftime('%d/%m/%Y')} às {self.horario_inicio.strftime('%H:%M')}"


#Agenda teleconsultas
class AgendaTeleconsulta(AgendaBase):
    medico = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True, blank=False, limit_choices_to={'role': 'medico'})

    def tem_procedimento_ativo(self):
        return self.teleconsultas.exclude(status='cancelada').exists()
    
    def __str__(self):
        return f"{self.medico.get_full_name()} - {self.data.strftime('%d/%m/%Y')} às {self.horario_inicio.strftime('%H:%M')}"
    
#Classe abstrata para reaproveitas informações para exames, consultas e teleconsultas
class AtendimentoBase(models.Model):
    STATUS_CHOICES = [
        ('agendada', 'Agendada'),
        ('cancelada', 'Cancelada'),
        ('em_andamento', 'Em atendimento'),
        ('finalizada', 'Finalizada'),
    ]

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='agendada')
    observacoes_visiveis = models.TextField(blank=True, null=True)
    observacoes_internas = models.TextField(blank=True, null=True)
    encaminhamento = models.TextField(blank=True, null=True)

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    motivo_cancelamento = models.TextField(blank=True, null=True)
    data_cancelamento = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

#Classe Consulta    
class Consulta(AtendimentoBase):
    agenda = models.ForeignKey(
        'AgendaConsulta',
        on_delete=models.PROTECT,
        related_name='consultas'
    )
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
    cancelado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='consultas_canceladas'
    )
    valor = models.DecimalField(max_digits=8, decimal_places=2, default=250.00)

    def __str__(self):
        return f"Consulta de {self.paciente.get_full_name()} com {self.medico.get_full_name()} em {self.agenda.data} às {self.agenda.horario_inicio}"

#Classe Teleconsulta    
class Teleconsulta(AtendimentoBase):
    agenda = models.ForeignKey(
        'AgendaTeleconsulta',
        on_delete=models.PROTECT,
        related_name='teleconsultas'
    )
    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'medico'},
        related_name='teleconsultas_como_medico'
    )
    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'paciente'},
        related_name='teleconsultas_como_paciente'
    )
    cancelado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teleconsultas_canceladas'
    )
    valor = models.DecimalField(max_digits=8, decimal_places=2, default=125.00)

    def __str__(self):
        return f"Teleconsulta de {self.paciente.get_full_name()} com {self.medico.get_full_name()} em {self.agenda.data} às {self.agenda.horario_inicio}"

#Classe Exame
class Exame(AtendimentoBase):
    TIPO_CHOICES = [
        ('radiografia', 'Radiografia (Raio-X)'),
        ('ultrassonografia', 'Ultrassonografia'),
        ('tomografia', 'Tomografia Computadorizada (TC)'),
        ('mamografia', 'Mamografia'),
        ('doppler', 'Doppler (Ultrassom Vascular)'),
    ]
    VALORES = {
        'radiografia': 250.00,
        'ultrassonografia': 300.00,
        'tomografia': 800.00,
        'mamografia': 400.00,
        'doppler': 500.00,
    }

    agenda = models.ForeignKey(
        'AgendaExame',
        on_delete=models.PROTECT,
        related_name='exames'
    )
    tipo = models.CharField(max_length=30, choices=TIPO_CHOICES)
    valor = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    medico = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'medico'},
        null=True, blank=True,
        related_name='exames_como_medico'
    )
    paciente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'paciente'},
        related_name='exames_como_paciente'
    )
    cancelado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='exames_cancelados'
    )

    def save(self, *args, **kwargs):
        if not self.valor:
            self.valor = self.VALORES.get(self.tipo, 0.00)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Exame de {self.get_tipo_display()} para {self.paciente.get_full_name()} em {self.agenda.data}"
    
#Classe para criação de laudos, atestados e receitas
# Documentos médicos genéricos (válido para Consulta ou Teleconsulta)

class Laudo(models.Model):
    consulta = models.ForeignKey(
        'Consulta', on_delete=models.CASCADE,
        related_name='laudos', null=True, blank=True
    )
    teleconsulta = models.ForeignKey(
        'Teleconsulta', on_delete=models.CASCADE,
        related_name='laudos', null=True, blank=True
    )
    medico = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        limit_choices_to={'role': 'medico'},
        related_name='laudos_emitidos'
    )
    paciente = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        limit_choices_to={'role': 'paciente'},
        related_name='laudos_recebidos'
    )
    conteudo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    arquivo_pdf = models.FileField(upload_to='documentos/laudos/', null=True, blank=True)

    def __str__(self):
        tipo = "Teleconsulta" if self.teleconsulta else "Consulta"
        return f"Laudo ({tipo}) - {self.paciente.get_full_name()}"


class Receita(models.Model):
    consulta = models.ForeignKey(
        'Consulta', on_delete=models.CASCADE,
        related_name='receitas', null=True, blank=True
    )
    teleconsulta = models.ForeignKey(
        'Teleconsulta', on_delete=models.CASCADE,
        related_name='receitas', null=True, blank=True
    )
    medico = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        limit_choices_to={'role': 'medico'},
        related_name='receitas_emitidas'
    )
    paciente = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        limit_choices_to={'role': 'paciente'},
        related_name='receitas_recebidas'
    )
    conteudo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    arquivo_pdf = models.FileField(upload_to='documentos/receitas/', null=True, blank=True)

    def __str__(self):
        tipo = "Teleconsulta" if self.teleconsulta else "Consulta"
        return f"Receita ({tipo}) - {self.paciente.get_full_name()}"


class Atestado(models.Model):
    consulta = models.ForeignKey(
        'Consulta', on_delete=models.CASCADE,
        related_name='atestados', null=True, blank=True
    )
    teleconsulta = models.ForeignKey(
        'Teleconsulta', on_delete=models.CASCADE,
        related_name='atestados', null=True, blank=True
    )
    medico = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        limit_choices_to={'role': 'medico'},
        related_name='atestados_emitidos'
    )
    paciente = models.ForeignKey(
        Usuario, on_delete=models.CASCADE,
        limit_choices_to={'role': 'paciente'},
        related_name='atestados_recebidos'
    )
    conteudo = models.TextField()
    criado_em = models.DateTimeField(auto_now_add=True)
    arquivo_pdf = models.FileField(upload_to='documentos/atestados/', null=True, blank=True)

    def __str__(self):
        tipo = "Teleconsulta" if self.teleconsulta else "Consulta"
        return f"Atestado ({tipo}) - {self.paciente.get_full_name()}"

#Model para a criação de um prontuário para o paciente
class Prontuario(models.Model):
    paciente = models.OneToOneField(Usuario, on_delete=models.CASCADE, limit_choices_to={'role': 'paciente'})
    alergias = models.TextField(blank=True)
    tratamentos = models.TextField(blank=True)
    historico_cirurgias = models.TextField(blank=True)
    observacoes_medicas = models.TextField(blank=True)

    def __str__(self):
        return f"Prontuário de {self.paciente.get_full_name()}"
    
#model para apresentação de laudos de resultados de exame
class ResultadoExame(models.Model):
    conteudo = models.TextField()
    medico = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='resultados_exames')
    paciente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='resultados_exames_paciente')
    exame = models.ForeignKey('Exame', on_delete=models.CASCADE, related_name='resultados')
    imagem = models.ImageField(upload_to='resultados_exames_imagens/', null=True, blank=True)  
    criado_em = models.DateTimeField(auto_now_add=True)
    arquivo_pdf = models.FileField(upload_to='documentos/resultados_exames/', null=True, blank=True)

class ImagemResultadoExame(models.Model):
    resultado = models.ForeignKey(ResultadoExame, on_delete=models.CASCADE, related_name='imagens')
    imagem = models.ImageField(upload_to='resultados_exames_imagens/')

#classe para receber informações de receita financeira
class ReceitaFinanceira(models.Model):
    PROCEDIMENTO_CHOICES = [
        ('consulta', 'Consulta Presencial'),
        ('teleconsulta', 'Teleconsulta'),
        ('exame', 'Exame'),
    ]

    procedimento = models.CharField(max_length=20, choices=PROCEDIMENTO_CHOICES)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_procedimento_display()} - R$ {self.valor:.2f} em {self.data.strftime('%d/%m/%Y')}"
    
#Criação da classe material
class Material(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    valor_unitario = models.DecimalField(max_digits=8, decimal_places=2)
    fornecedor = models.CharField(max_length=100)

    def __str__(self):
        return self.nome
    
#Criação da classe estoque
class Estoque(models.Model):
    material = models.OneToOneField(Material, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.material.nome} - {self.quantidade} un"

#Criação do modelo para gerar pedidos de materiais
class PedidoMaterial(models.Model):
    STATUS_CHOICES = [
        ('pendente', 'Pendente de aprovação'),
        ('aprovado', 'Compra aprovada'),
        ('entregue', 'Material entregue'),
    ]

    material = models.ForeignKey(Material, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    valor_total = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='pedidos_materiais_criados'
    )
    data_pedido = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    data_aprovacao = models.DateTimeField(null=True, blank=True)
    aprovado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pedidos_materiais_aprovados'
    )

    data_entrega = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.material.nome} - {self.quantidade} un - {self.get_status_display()}"

#classe para armazenar informações dos pagamentos efetuados
class Pagamento(models.Model):
    descricao = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=8, decimal_places=2)
    data_pagamento = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.descricao} - R$ {self.valor:.2f}"
