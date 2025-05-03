from datetime import timedelta, datetime
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Sala, Agenda, Consulta, Usuario
from .forms import SalaForm, AgendaForm, ConsultaForm
from .decorators import role_required
from django import forms



#View criada para o correto direcionamento de página inicial conforme o perfil de usuário
@login_required
def redirecionar_dashboard(request):
    usuario = request.user

    if usuario.role == 'paciente':
        return redirect('dashboard_paciente')
    elif usuario.role == 'medico':
        return redirect('dashboard_medico')
    elif usuario.role == 'administrativo':
        return redirect('dashboard_administrativo')
    elif usuario.role == 'financeiro':
        return redirect('dashboard_financeiro')
    
    return redirect('login')

@role_required('paciente')
def dashboard_paciente(request):
    return render(request, 'dashboard/paciente.html')

@role_required('medico')
def dashboard_medico(request):
    return render(request, 'dashboard/medico.html')

@role_required('administrativo')
def dashboard_administrativo(request):
    return render(request, 'dashboard/administrativo.html')

@role_required('financeiro')
def dashboard_financeiro(request):
    return render(request, 'dashboard/financeiro.html')

# Exibir lista de salas
@role_required('administrativo')
def lista_salas(request):
    salas = Sala.objects.all()
    return render(request, 'estrutura/lista_salas.html', {'salas': salas})

# Adicionar nova sala
@role_required('administrativo')
def adicionar_sala(request):
    form = SalaForm(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_salas')
    return render(request, 'estrutura/form_sala.html', {'form': form})

# Editar sala existente
@role_required('administrativo')
def editar_sala(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
    form = SalaForm(request.POST or None, instance=sala)
    if form.is_valid():
        form.save()
        return redirect('lista_salas')
    return render(request, 'estrutura/form_sala.html', {'form': form})

# Excluir sala
@role_required('administrativo')
def excluir_sala(request, pk):
    sala = get_object_or_404(Sala, pk=pk)
    if request.method == 'POST':
        sala.delete()
        return redirect('lista_salas')
    return render(request, 'estrutura/confirmar_exclusao.html', {'sala': sala})

#listar agenda
@role_required('administrativo')
def lista_agenda(request):
    agendas = Agenda.objects.order_by('data', 'horario_inicio')
    return render(request, 'agenda/lista_agenda.html', {'agendas': agendas})

#Criar agenda
@role_required('administrativo')
def criar_agenda(request):
    if request.method == 'POST':
        form = AgendaForm(request.POST)
        if form.is_valid():
            base_agenda = form.save(commit=False)

            inicio = datetime.combine(base_agenda.data, base_agenda.horario_inicio)
            fim = datetime.combine(base_agenda.data, base_agenda.horario_fim)
            duracao = timedelta(minutes=base_agenda.duracao_procedimento)

            horarios = []
            atual = inicio

            conflitos = []

            while atual + duracao <= fim:
                horario_fim = atual + duracao

                # Verifica conflito de sala
                conflito_sala = Agenda.objects.filter(
                    sala=base_agenda.sala,
                    data=base_agenda.data,
                    horario_inicio__lt=horario_fim,
                    horario_fim__gt=atual,
                ).exists()

                # Verifica conflito de médico (se houver médico)
                conflito_medico = False
                if base_agenda.medico:
                    conflito_medico = Agenda.objects.filter(
                        medico=base_agenda.medico,
                        data=base_agenda.data,
                        horario_inicio__lt=horario_fim,
                        horario_fim__gt=atual,
                    ).exists()

                if conflito_sala or conflito_medico:
                    conflitos.append(atual.strftime("%H:%M"))

                else:
                    nova = Agenda(
                        procedimento=base_agenda.procedimento,
                        tipo_exame=base_agenda.tipo_exame,
                        medico=base_agenda.medico,
                        sala=base_agenda.sala,
                        data=base_agenda.data,
                        horario_inicio=atual.time(),
                        horario_fim=horario_fim.time(),
                        duracao_procedimento=base_agenda.duracao_procedimento
                    )
                    nova.save()

                atual += duracao

            if conflitos:
                messages.warning(request, f"Horários ignorados por conflito: {', '.join(conflitos)}")
            else:
                messages.success(request, "Horários criados com sucesso!")

            return redirect('lista_agenda')
    else:
        form = AgendaForm()

    return render(request, 'agenda/form_agenda.html', {'form': form})

#Editar Agenda
@role_required('administrativo')
def editar_agenda(request, pk):
    agenda = get_object_or_404(Agenda, pk=pk)
    form = AgendaForm(request.POST or None, instance=agenda)
    if form.is_valid():
        form.save()
        return redirect('lista_agenda')
    return render(request, 'agenda/form_agenda.html', {'form': form})

#Excluir Agenda
@role_required('administrativo')
def excluir_agenda(request, pk):
    agenda = get_object_or_404(Agenda, pk=pk)

    # Checa se está agendada (ajuste depois conforme sua lógica de agendamento)
    if hasattr(agenda, 'consulta') or hasattr(agenda, 'exame'):
        messages.error(request, 'Não é possível excluir um horário agendado. Cancele o agendamento antes.')
        return redirect('lista_agenda')

    if request.method == 'POST':
        agenda.delete()
        return redirect('lista_agenda')

    return render(request, 'agenda/excluir_agenda.html', {'agenda': agenda})

#Função para redirecionar a pagina quando usuário tenta acessar pagina sem permissão de acesso
def erro_403(request, exception=None):
    return render(request, '403.html', status=403)

#View para agendamento de consultas
@role_required('administrativo', 'paciente')
def agendar_consulta(request):
    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            consulta = form.save(commit=False)

            # Verifica se o bloco de agenda está disponível
            agenda = consulta.agenda
            if agenda.procedimento != 'consulta' or agenda.status == "Agendado":
                messages.error(request, 'Horário indisponível.')
                return redirect('agendar_consulta')

            # Verifica se o médico do agendamento bate com o da agenda
            if consulta.medico != agenda.medico:
                messages.error(request, 'O médico selecionado não atende neste horário.')
                return redirect('agendar_consulta')

            # Verifica se o paciente já tem outro procedimento no mesmo horário
            conflito = Consulta.objects.filter(paciente=consulta.paciente, agenda=agenda).exists()
            if conflito:
                messages.error(request, 'Já existe uma consulta agendada neste horário.')
                return redirect('agendar_consulta')

            # Marca a agenda como ocupada e salva a consulta
            agenda.ocupado = True
            agenda.save()
            consulta.valor = 250.00
            consulta.save()

            messages.success(request, 'Consulta agendada com sucesso.')
            return redirect('dashboard_paciente' if request.user.role == 'paciente' else 'dashboard_administrativo')
    else:
        form = ConsultaForm()
        # Se for paciente, oculta o campo paciente
        if request.user.role == 'paciente':
            form.fields['paciente'].initial = request.user
            form.fields['paciente'].widget = forms.HiddenInput()

    return render(request, 'consultas/form_agendamento.html', {'form': form})

#View para a listagem de consultas
@role_required('paciente', 'administrativo', 'medico')
def lista_consultas(request):
    usuario = request.user
    if usuario.role == 'paciente':
        consultas = Consulta.objects.filter(paciente=usuario).order_by('-agenda__data')
    elif usuario.role == 'medico':
        consultas = Consulta.objects.filter(medico=usuario).order_by('-agenda__data')
    elif usuario.role == 'administrativo':
        consultas = Consulta.objects.all().order_by('-agenda__data')
    else:
        consultas = []

    return render(request, 'consultas/lista_consultas.html', {'consultas': consultas})