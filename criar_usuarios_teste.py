# criar_usuarios_teste.py

import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SHGSS.settings')  # ajuste se necessário
django.setup()

User = get_user_model()

usuarios_teste = [
    {
        'username': 'paciente1',
        'email': 'pac@email.com',
        'password': 'Teste123*',
        'role': 'paciente',
        'cpf': '000.111.222-33',
        'telefone': '(41) 99999-0000',
        'rua': 'Rua das Flores',
        'numero': '123',
        'bairro': 'Centro',
        'cidade': 'Curitiba',
        'estado': 'PR',
        'cep': '80000-000',
        'plano_saude': 'Unimed',
        'numero_cartao_plano': '1234567890',
    },
    {
        'username': 'medico1',
        'email': 'medico@email.com',
        'password': 'Teste123*',
        'role': 'medico',
        'cpf': '111.222.333-44',
        'telefone': '(41) 98888-0000',
        'rua': 'Av. Saúde',
        'numero': '456',
        'bairro': 'Boa Vista',
        'cidade': 'Curitiba',
        'estado': 'PR',
        'cep': '80001-000',
        'crm': 'CRM123456',
        'especialidade': 'Clínico Geral',
    },
    {
        'username': 'admin1',
        'email': 'admin@email.com',
        'password': 'Teste123*',
        'role': 'administrativo',
        'cpf': '222.333.444-55',
        'telefone': '(41) 97777-0000',
        'rua': 'Rua Admin',
        'numero': '789',
        'bairro': 'Água Verde',
        'cidade': 'Curitiba',
        'estado': 'PR',
        'cep': '80002-000',
        'setor': 'Atendimento',
        'cargo': 'Secretário',
    },
    {
        'username': 'financeiro1',
        'email': 'fin@email.com',
        'password': 'Teste123*',
        'role': 'financeiro',
        'cpf': '333.444.555-66',
        'telefone': '(41) 96666-0000',
        'rua': 'Rua Financeiro',
        'numero': '101',
        'bairro': 'Batel',
        'cidade': 'Curitiba',
        'estado': 'PR',
        'cep': '80003-000',
        'setor': 'Contabilidade',
        'cargo': 'Financeiro',
    },
]

for dados in usuarios_teste:
    if not User.objects.filter(username=dados['username']).exists():
        senha = dados.pop('password')
        user = User.objects.create_user(**dados)
        user.set_password(senha)
        user.save()
        print(f"✅ Usuário {user.username} criado com sucesso!")
    else:
        print(f"ℹ️ Usuário {dados['username']} já existe.")
