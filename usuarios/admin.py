from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario, Consulta

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario

    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_active')

    # Formulário de edição (usuário existente)
    fieldsets = UserAdmin.fieldsets + (
        ("Informações Pessoais", {
            "fields": (
                'cpf', 'telefone', 'rua', 'numero', 'bairro', 'cidade', 'estado', 'cep',
                'role', 'plano_saude', 'numero_cartao_plano', 'crm', 'especialidade',
                'setor', 'cargo'
            )
        }),
    )

    # Formulário de criação (novo usuário)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'cpf', 'role'),
        }),
    )

@admin.register(Consulta)
class ConsultaAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'medico', 'agenda', 'status', 'criado_em')
    list_filter = ('status', 'medico', 'paciente')
