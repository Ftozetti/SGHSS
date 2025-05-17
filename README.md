# 🏥 SGHSS – Sistema de Gestão Hospitalar e de Serviços de Saúde

Este sistema é um projeto com fins educacionais, desenvolvido com Django no contexto do curso de Análise e Desenvolvimento de Sistemas da **UNINTER – Centro Universitário Internacional**.  
O objetivo é demonstrar, na prática, a construção de um sistema completo de gestão para clínicas médicas, com múltiplos perfis de usuários e funcionalidades específicas: **Paciente, Médico, Administrativo e Financeiro**.

⚠️ **Este sistema não deve ser utilizado em ambiente de produção real**.  
No entanto, o código está disponível e pode ser usado, adaptado ou estudado livremente pela comunidade.

---

## 🚀 Funcionalidades principais

- Agendamento e cancelamento de **consultas, exames e teleconsultas**
- Geração de **laudos, receitas e atestados** em PDF
- Visualização de **prontuário médico**
- Gestão de **estoque de materiais e pedidos**
- Controle de **receitas financeiras**
- Interface diferenciada para cada perfil de usuário

---

## 🛠️ Como rodar o sistema

### 1. Clonar o repositório

#### Por meio do Powershell ou do Prompt de Comando, abra a pasta, na qual deseja clonar o repositorio
```bash
git clone https://github.com/Ftozetti/SGHSS

```

### 2. Criar e ativar ambiente virtual

#### Dentro da pasta onde o repositorio foi criada, execute o comando para criar e ativar ambiente virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac
```

### 3. Instalar dependências

```bash
pip install -r requirements.txt
```

### 4. Criar o banco de dados

```bash
python manage.py migrate
```

---

## 👤 Criar usuários para testes e incluir materiais no banco de dados para testes

Para facilitar a avaliação do sistema, execute o script abaixo para gerar usuários de todos os perfis com todos os **campos obrigatórios preenchidos** (como CPF, endereço, CRM, setor etc.):

```bash
python configuracoes_iniciais_teste.py
```

### 🧪 Usuários criados automaticamente:

| Perfil         | Usuário         | Senha      |
|----------------|-----------------|------------|
| Paciente       | `paciente1`     | `Teste123*`|
| Médico         | `medico1`       | `Teste123*`|
| Administrativo | `admin1`        | `Teste123*`|
| Financeiro     | `financeiro1`   | `Teste123*`|

Esses usuários já estarão com todos os dados obrigatórios preenchidos conforme exigido pela model `Usuario`.

---

## ▶️ Executar o servidor

```bash
python manage.py runserver
```

Acesse no navegador: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📂 Estrutura do projeto

- `manage.py` – ponto de entrada do Django
- `SGHSS/` – configurações do projeto
- `usuarios/` – app principal com views, models, forms
- `templates/` – HTMLs organizados por módulo
- `media/` – PDFs gerados (receitas, laudos, etc.)
- `criar_usuarios_teste.py` – script para criar usuários de exemplo

---

## 📌 Observações

- O projeto usa SQLite por padrão.
- Para manter os arquivos gerados (PDFs), não esqueça de copiar a pasta `media/` ao trocar de máquina.