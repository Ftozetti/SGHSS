from datetime import timedelta, datetime
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import (Sala, Consulta, Usuario, Prontuario, Exame, Teleconsulta, Laudo, 
    Receita, Atestado, AgendaConsulta, AgendaExame, AgendaTeleconsulta, ResultadoExame,
    ImagemResultadoExame
)
from .forms import (SalaForm, ConsultaForm, CancelamentoConsultaForm, LaudoForm, 
                    ReceitaForm, AtestadoForm, ProntuarioForm, ObservacoesConsultaForm, 
                    SelecionarPacienteForm, ExameForm, AgendaExameForm, AgendaTeleconsultaForm, 
                    AgendaConsultaForm, AgendaTeleconsulta, TeleconsultaForm, ResultadoExameForm 
)
from .decorators import role_required
from django import forms
from django.template.loader import render_to_string
from django.http import HttpResponse, FileResponse, HttpResponseForbidden, JsonResponse
from xhtml2pdf import pisa
import io
from django.core.files.base import ContentFile



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

#Criação de agenda de consultas
@role_required('administrativo')
def criar_agenda_consulta(request):
    if request.method == 'POST':
        form = AgendaConsultaForm(request.POST)
        if form.is_valid():
            base_agenda = form.save(commit=False)

            inicio = datetime.combine(base_agenda.data, base_agenda.horario_inicio)
            fim = datetime.combine(base_agenda.data, base_agenda.horario_fim)
            duracao = timedelta(minutes=base_agenda.duracao_procedimento)

            atual = inicio
            conflitos = []

            while atual + duracao <= fim:
                horario_fim = atual + duracao

                conflito_sala = AgendaConsulta.objects.filter(
                    sala=base_agenda.sala,
                    data=base_agenda.data,
                    horario_inicio__lt=horario_fim,
                    horario_fim__gt=atual,
                ).exists()

                conflito_medico = False
                if base_agenda.medico:
                    conflito_medico = AgendaConsulta.objects.filter(
                        medico=base_agenda.medico,
                        data=base_agenda.data,
                        horario_inicio__lt=horario_fim,
                        horario_fim__gt=atual,
                    ).exists()

                if conflito_sala or conflito_medico:
                    conflitos.append(atual.strftime("%H:%M"))
                else:
                    nova = AgendaConsulta(
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

            return redirect('lista_agenda_consulta')
    else:
        form = AgendaConsultaForm()

    return render(request, 'agenda/form_agenda.html', {'form': form, 'tipo': 'consulta'})

#Criar agenda de exames
@role_required('administrativo')
def criar_agenda_exame(request):
    if request.method == 'POST':
        form = AgendaExameForm(request.POST)
        if form.is_valid():
            base_agenda = form.save(commit=False)

            inicio = datetime.combine(base_agenda.data, base_agenda.horario_inicio)
            fim = datetime.combine(base_agenda.data, base_agenda.horario_fim)
            duracao = timedelta(minutes=base_agenda.duracao_procedimento)

            atual = inicio
            conflitos = []

            while atual + duracao <= fim:
                horario_fim = atual + duracao

                conflito_sala = AgendaExame.objects.filter(
                    sala=base_agenda.sala,
                    data=base_agenda.data,
                    horario_inicio__lt=horario_fim,
                    horario_fim__gt=atual,
                ).exists()

                conflito_medico = False
                if base_agenda.medico:
                    conflito_medico = AgendaExame.objects.filter(
                        medico=base_agenda.medico,
                        data=base_agenda.data,
                        horario_inicio__lt=horario_fim,
                        horario_fim__gt=atual,
                    ).exists()

                if conflito_sala or conflito_medico:
                    conflitos.append(atual.strftime("%H:%M"))
                else:
                    nova = AgendaExame(
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
                messages.success(request, "Horários de exame criados com sucesso!")

            return redirect('lista_agenda_exame')
    else:
        form = AgendaExameForm()

    return render(request, 'agenda/form_agenda.html', {'form': form, 'tipo': 'exame'})

#Criar agenda de Teleconsultas
@role_required('administrativo')
def criar_agenda_teleconsulta(request):
    if request.method == 'POST':
        form = AgendaTeleconsultaForm(request.POST)
        if form.is_valid():
            base_agenda = form.save(commit=False)

            inicio = datetime.combine(base_agenda.data, base_agenda.horario_inicio)
            fim = datetime.combine(base_agenda.data, base_agenda.horario_fim)
            duracao = timedelta(minutes=base_agenda.duracao_procedimento)

            atual = inicio
            conflitos = []

            while atual + duracao <= fim:
                horario_fim = atual + duracao

                conflito_medico = AgendaTeleconsulta.objects.filter(
                    medico=base_agenda.medico,
                    data=base_agenda.data,
                    horario_inicio__lt=horario_fim,
                    horario_fim__gt=atual,
                ).exists()

                if conflito_medico:
                    conflitos.append(atual.strftime("%H:%M"))
                else:
                    nova = AgendaTeleconsulta(
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
                messages.success(request, "Horários de teleconsulta criados com sucesso!")

            return redirect('lista_agenda_teleconsulta')
    else:
        form = AgendaTeleconsultaForm()

    return render(request, 'agenda/form_agenda.html', {'form': form, 'tipo': 'teleconsulta'})

#Editar Agenda de consultas
@role_required('administrativo')
def editar_agenda_consulta(request, pk):
    agenda = get_object_or_404(AgendaConsulta, pk=pk)

    if agenda.consultas.exclude(status='cancelada').exists():
        messages.error(request, 'Não é possível editar um horário com consultas ativas.')
        return redirect('lista_agenda_consulta')

    form = AgendaConsultaForm(request.POST or None, instance=agenda)
    if form.is_valid():
        form.save()
        return redirect('lista_agenda_consulta')

    return render(request, 'agenda/form_agenda.html', {'form': form})

#Editar Agenda de exames
@role_required('administrativo')
def editar_agenda_exame(request, pk):
    agenda = get_object_or_404(AgendaExame, pk=pk)

    if agenda.exames.exclude(status='cancelada').exists():
        messages.error(request, 'Não é possível editar um horário com exames agendados.')
        return redirect('lista_agenda_exame')

    form = AgendaExameForm(request.POST or None, instance=agenda)
    if form.is_valid():
        form.save()
        return redirect('lista_agenda_exame')

    return render(request, 'agenda/form_agenda.html', {'form': form})

#Editar agenda de teleconsulta
@role_required('administrativo')
def editar_agenda_teleconsulta(request, pk):
    agenda = get_object_or_404(AgendaTeleconsulta, pk=pk)

    if agenda.teleconsultas.exclude(status='cancelada').exists():
        messages.error(request, 'Não é possível editar um horário com teleconsultas ativas.')
        return redirect('lista_agenda_teleconsulta')

    form = AgendaTeleconsultaForm(request.POST or None, instance=agenda)
    if form.is_valid():
        form.save()
        return redirect('lista_agenda_teleconsulta')

    return render(request, 'agenda/form_agenda.html', {'form': form})

#Excluir Agenda de consultas
@role_required('administrativo')
def excluir_agenda_consulta(request, pk):
    agenda = get_object_or_404(AgendaConsulta, pk=pk)

    if agenda.consultas.exists():
        messages.error(request, 'Não é possível excluir um horário com consulta agendada.')
        return redirect('lista_agenda_consulta')

    if request.method == 'POST':
        agenda.delete()
        return redirect('lista_agenda_consulta')

    return render(request, 'agenda/excluir_agenda.html', {'agenda': agenda})

#Excluir Agenda de exame
@role_required('administrativo')
def excluir_agenda_exame(request, pk):
    agenda = get_object_or_404(AgendaExame, pk=pk)

    if agenda.exames.exists():
        messages.error(request, 'Não é possível excluir um horário com exame agendado.')
        return redirect('lista_agenda_exame')

    if request.method == 'POST':
        agenda.delete()
        return redirect('lista_agenda_exame')

    return render(request, 'agenda/excluir_agenda.html', {'agenda': agenda})

#Excluir Agenda de teleconsulta
@role_required('administrativo')
def excluir_agenda_teleconsulta(request, pk):
    agenda = get_object_or_404(AgendaTeleconsulta, pk=pk)

    if agenda.teleconsultas.exists():
        messages.error(request, 'Não é possível excluir um horário com teleconsulta agendada.')
        return redirect('lista_agenda_teleconsulta')

    if request.method == 'POST':
        agenda.delete()
        return redirect('lista_agenda_teleconsulta')

    return render(request, 'agenda/excluir_agenda.html', {'agenda': agenda})

#Bloqueio/Desbloqueio manual de Agenda de consultas
@role_required('administrativo')
def bloquear_agenda_consulta(request, pk):
    agenda = get_object_or_404(AgendaConsulta, pk=pk)
    
    if agenda.consultas.exclude(status='cancelada').exists():
        messages.error(
            request,
            'Este horário está vinculado a uma consulta ativa. '
            'Para bloqueá-lo, cancele primeiro a consulta correspondente.'
        )
        return redirect('lista_agenda_consulta')

    agenda.status_manual = 'bloqueado'
    agenda.save()
    messages.success(request, 'Horário bloqueado com sucesso.')
    return redirect('lista_agenda_consulta')


@role_required('administrativo')
def desbloquear_agenda_consulta(request, pk):
    agenda = get_object_or_404(AgendaConsulta, pk=pk)

    if agenda.consultas.exclude(status='cancelada').exists():
        messages.error(
            request,
            'Não é possível desbloquear este horário, pois há uma consulta ativa vinculada.'
        )
        return redirect('lista_agenda_consulta')

    agenda.status_manual = 'livre'
    agenda.save()
    messages.success(request, 'Horário desbloqueado com sucesso.')
    return redirect('lista_agenda_consulta')

#Bloqueio/Desbloqueio manual de Agenda de exames
@role_required('administrativo')
def bloquear_agenda_exame(request, pk):
    agenda = get_object_or_404(AgendaExame, pk=pk)

    if agenda.exames.exclude(status='cancelada').exists():
        messages.error(
            request,
            'Este horário já possui um exame agendado. '
            'Cancele o exame antes de bloquear o horário.'
        )
        return redirect('lista_agenda_exame')

    agenda.status_manual = 'bloqueado'
    agenda.save()
    messages.success(request, 'Horário de exame bloqueado com sucesso.')
    return redirect('lista_agenda_exame')


@role_required('administrativo')
def desbloquear_agenda_exame(request, pk):
    agenda = get_object_or_404(AgendaExame, pk=pk)

    if agenda.exames.exclude(status='cancelada').exists():
        messages.error(
            request,
            'Não é possível desbloquear este horário, pois há um exame ativo vinculado.'
        )
        return redirect('lista_agenda_exame')

    agenda.status_manual = 'livre'
    agenda.save()
    messages.success(request, 'Horário de exame desbloqueado com sucesso.')
    return redirect('lista_agenda_exame')


#Bloqueio/Desbloqueio manual de Agenda de teleconsultas
@role_required('administrativo')
def bloquear_agenda_teleconsulta(request, pk):
    agenda = get_object_or_404(AgendaTeleconsulta, pk=pk)

    if agenda.teleconsultas.exclude(status='cancelada').exists():
        messages.error(
            request,
            'Este horário já está reservado para uma teleconsulta. '
            'É necessário cancelar a teleconsulta para que o horário possa ser bloqueado.'
        )
        return redirect('lista_agenda_teleconsulta')

    agenda.status_manual = 'bloqueado'
    agenda.save()
    messages.success(request, 'Horário de teleconsulta bloqueado com sucesso.')
    return redirect('lista_agenda_teleconsulta')


@role_required('administrativo')
def desbloquear_agenda_teleconsulta(request, pk):
    agenda = get_object_or_404(AgendaTeleconsulta, pk=pk)

    if agenda.teleconsultas.exclude(status='cancelada').exists():
        messages.error(
            request,
            'Não é possível desbloquear este horário, pois há uma teleconsulta ativa vinculada.'
        )
        return redirect('lista_agenda_teleconsulta')

    agenda.status_manual = 'livre'
    agenda.save()
    messages.success(request, 'Horário de teleconsulta desbloqueado com sucesso.')
    return redirect('lista_agenda_teleconsulta')


#Lista de agenda de consultas
@role_required('administrativo')
def lista_agenda_consulta(request):
    agendas = AgendaConsulta.objects.order_by('data', 'horario_inicio')
    for a in agendas:
        a.tem_consulta_ativa = a.consultas.exclude(status='cancelada').exists()
    return render(request, 'agenda/lista_agenda_consulta.html', {'agendas': agendas})

#Lista de agenda de Exames
@role_required('administrativo')
def lista_agenda_exame(request):
    agendas = AgendaExame.objects.order_by('data', 'horario_inicio')
    for a in agendas:
        a.tem_exame_ativo = a.exames.exclude(status='cancelada').exists()
    return render(request, 'agenda/lista_agenda_exame.html', {'agendas': agendas})

#Lista de agenda de Teleconsultas
@role_required('administrativo')
def lista_agenda_teleconsulta(request):
    agendas = AgendaTeleconsulta.objects.order_by('data', 'horario_inicio')
    for a in agendas:
        a.tem_teleconsulta_ativa = a.teleconsultas.exclude(status='cancelada').exists()
    return render(request, 'agenda/lista_agenda_teleconsulta.html', {'agendas': agendas})

#View para agendamento de consultas
@role_required('administrativo', 'paciente')
def agendar_consulta(request):
    if request.method == 'POST':
        form = ConsultaForm(request.POST)
        if form.is_valid():
            consulta = form.save(commit=False)
            agenda = consulta.agenda  # Deve ser uma instância de AgendaConsulta

            # Validação 1: agenda deve ser uma AgendaConsulta válida e disponível
            if not isinstance(agenda, AgendaConsulta) or not agenda.esta_disponivel:
                messages.error(request, 'Horário indisponível para agendamento.')
                return redirect('agendar_consulta')

            # Validação 2: médico da consulta deve coincidir com o da agenda
            if consulta.medico != agenda.medico:
                messages.error(request, 'O médico selecionado não atende neste horário.')
                return redirect('agendar_consulta')

            # Validação 3: paciente não pode ter outra consulta no mesmo horário
            conflito = Consulta.objects.filter(
                paciente=consulta.paciente,
                agenda__data=agenda.data,
                agenda__horario_inicio=agenda.horario_inicio
            ).exclude(status='cancelada').exists()

            if conflito:
                messages.error(request, 'Você já possui uma consulta nesse mesmo horário.')
                return redirect('agendar_consulta')

            # Se passou em todas as validações, salva a consulta
            consulta.valor = 250.00
            consulta.save()

            messages.success(request, 'Consulta agendada com sucesso.')
            return redirect('dashboard_paciente' if request.user.role == 'paciente' else 'dashboard_administrativo')
    else:
        form = ConsultaForm()
        if request.user.role == 'paciente':
            form.fields['paciente'].initial = request.user
            form.fields['paciente'].widget = forms.HiddenInput()

    return render(request, 'consultas/form_agendamento.html', {'form': form})

#Agendamento de Exames
@role_required('administrativo', 'paciente')
def agendar_exame(request):
    if request.method == 'POST':
        form = ExameForm(request.POST, user=request.user)
        if form.is_valid():
            exame = form.save(commit=False)
            agenda = exame.agenda

            if not isinstance(agenda, AgendaExame) or not agenda.esta_disponivel:
                messages.error(request, 'Horário indisponível.')
                return redirect('agendar_exame')

            # Garante que paciente seja atribuído se for um paciente logado
            if request.user.role == 'paciente':
                exame.paciente = request.user

            # Define o valor conforme o tipo do exame
            exame.valor = Exame.VALORES.get(exame.tipo, 0.00)
            exame.save()

            messages.success(request, 'Exame agendado com sucesso.')
            return redirect('dashboard_paciente' if request.user.role == 'paciente' else 'dashboard_administrativo')
    else:
        form = ExameForm(user=request.user)

    return render(request, 'exames/form_agendamento.html', {'form': form})

#Agendamento de teleconsultas
@role_required('administrativo', 'paciente')
def agendar_teleconsulta(request):
    if request.method == 'POST':
        form = TeleconsultaForm(request.POST, user=request.user)
        if form.is_valid():
            tele = form.save(commit=False)
            agenda = tele.agenda

            # Atribui automaticamente o paciente se for paciente logado
            if request.user.role == 'paciente':
                tele.paciente = request.user

            if not isinstance(agenda, AgendaTeleconsulta) or not agenda.esta_disponivel:
                messages.error(request, 'Horário indisponível para agendamento.')
                return redirect('agendar_teleconsulta')

            if tele.medico != agenda.medico:
                messages.error(request, 'O médico selecionado não atende neste horário.')
                return redirect('agendar_teleconsulta')

            conflito = Teleconsulta.objects.filter(
                paciente=tele.paciente,
                agenda__data=agenda.data,
                agenda__horario_inicio=agenda.horario_inicio
            ).exclude(status='cancelada').exists()

            if conflito:
                messages.error(request, 'Você já possui uma teleconsulta neste horário.')
                return redirect('agendar_teleconsulta')

            tele.valor = 125
            tele.save()
            messages.success(request, 'Teleconsulta agendada com sucesso.')
            return redirect('dashboard_paciente' if request.user.role == 'paciente' else 'dashboard_administrativo')
    else:
        form = TeleconsultaForm(user=request.user)

    return render(request, 'teleconsultas/form_agendamento.html', {'form': form})

#View para a listagem de consultas para o medico
@role_required('medico')
def lista_consultas(request):
    consultas = Consulta.objects.filter(medico=request.user).order_by('-agenda__data')
    return render(request, 'consultas/lista_consultas.html', {'consultas': consultas})

#View para a listagem de teleconsultas para o medico
@role_required('medico')
def lista_teleconsultas(request):
    teleconsultas = Teleconsulta.objects.filter(medico=request.user).order_by('-agenda__data')
    return render(request, 'teleconsultas/lista_teleconsultas.html', {'teleconsultas': teleconsultas})


#view para cancelamento de consulta
@role_required('paciente', 'administrativo')
def cancelar_consulta(request, consulta_id):
    consulta = get_object_or_404(Consulta, pk=consulta_id)

    # Garante que pacientes só possam cancelar suas próprias consultas
    if request.user.role == 'paciente' and consulta.paciente != request.user:
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        consulta.status = 'cancelada'
        consulta.save()

        # Redireciona de acordo com o perfil
        if request.user.role == 'paciente':
            return redirect('consultas_usuario')
        elif request.user.role == 'administrativo':
            return redirect('consultas_usuario')

    form = CancelamentoConsultaForm()
    return render(request, 'consultas/cancelar_consulta.html', {'consulta': consulta, 'form': form})

#View para cancelar exame
@role_required('paciente', 'administrativo')
def cancelar_exame(request, exame_id):
    exame = get_object_or_404(Exame, pk=exame_id)

    if request.user.role == 'paciente' and exame.paciente != request.user:
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        exame.status = 'cancelada'
        exame.cancelado_por = request.user
        exame.data_cancelamento = timezone.now()
        exame.save()

        return redirect('exames_usuario')

    form = CancelamentoConsultaForm()
    return render(request, 'consultas/cancelar_consulta.html', {'consulta': exame, 'form': form})

#View para cancelar teleconsulta
@role_required('paciente', 'administrativo')
def cancelar_teleconsulta(request, teleconsulta_id):
    tele = get_object_or_404(Teleconsulta, pk=teleconsulta_id)

    if request.user.role == 'paciente' and tele.paciente != request.user:
        return render(request, '403.html', status=403)

    if request.method == 'POST':
        tele.status = 'cancelada'
        tele.cancelado_por = request.user
        tele.data_cancelamento = timezone.now()
        tele.save()

        return redirect('teleconsultas_usuario')

    form = CancelamentoConsultaForm()
    return render(request, 'consultas/cancelar_consulta.html', {'consulta': tele, 'form': form})

#View para iniciar consulta
@role_required('medico')
def iniciar_consulta(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk, medico=request.user)
    
    if consulta.status != 'agendada':
        messages.error(request, 'A consulta não pode ser iniciada.')
        return redirect('lista_consultas')

    consulta.status = 'em_andamento'
    consulta.save()
    
    return redirect('detalhar_consulta', pk=consulta.pk)

#view para detalhar a consulta
@role_required('medico')
def detalhar_consulta(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk, medico=request.user)

    if request.method == 'POST':
        form = ObservacoesConsultaForm(request.POST, instance=consulta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Observações atualizadas com sucesso.')
            return redirect('detalhar_consulta', pk=pk)
    else:
        form = ObservacoesConsultaForm(instance=consulta)

    return render(request, 'consultas/detalhar_consulta.html', {
        'consulta': consulta,
        'form_observacoes': form,
        'is_teleconsulta': False  
    })

#View que permite o cancelamento do atendimento e retorna o status para agendado
@role_required('medico')
def cancelar_atendimento(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk, medico=request.user)
    if request.method == 'POST' and consulta.status == 'em_andamento':
        consulta.status = 'agendada'
        consulta.save()
    return redirect('lista_consultas')

# view que encerra o atendimento e altera o status para finalizada
@role_required('medico')
def encerrar_atendimento(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk, medico=request.user)
    if request.method == 'POST' and consulta.status == 'em_andamento':
        consulta.status = 'finalizada'
        consulta.save()
    return redirect('lista_consultas') 

#View para emissão de laudo em pdf
@role_required('medico')
def emitir_laudo_consulta(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk, medico=request.user)
    paciente = consulta.paciente

    if request.method == 'POST':
        form = LaudoForm(request.POST)
        if form.is_valid():
            laudo = form.save(commit=False)
            laudo.consulta = consulta
            laudo.medico = request.user
            laudo.paciente = paciente
            laudo.save()

            html = render_to_string('consultas/laudo_pdf.html', {'laudo': laudo})
            resultado = io.BytesIO()
            pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=resultado)
            laudo.arquivo_pdf.save(f'laudo_{laudo.id}.pdf', ContentFile(resultado.getvalue()))
            laudo.save()

            return redirect('detalhar_consulta', pk=consulta.pk)
    else:
        form = LaudoForm()

    return render(request, 'consultas/form_laudo_consulta.html', {
        'consulta': consulta,
        'form': form
    })


@role_required('medico')
def emitir_laudo_teleconsulta(request, pk):
    teleconsulta = get_object_or_404(Teleconsulta, pk=pk, medico=request.user)
    paciente = teleconsulta.paciente

    if request.method == 'POST':
        form = LaudoForm(request.POST)
        if form.is_valid():
            laudo = form.save(commit=False)
            laudo.teleconsulta = teleconsulta
            laudo.medico = request.user
            laudo.paciente = paciente
            laudo.save()

            html = render_to_string('consultas/laudo_pdf.html', {'laudo': laudo})
            resultado = io.BytesIO()
            pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=resultado)
            laudo.arquivo_pdf.save(f'laudo_{laudo.id}.pdf', ContentFile(resultado.getvalue()))
            laudo.save()

            return redirect('detalhar_teleconsulta', pk=teleconsulta.pk)
    else:
        form = LaudoForm()

    return render(request, 'consultas/form_laudo_teleconsulta.html', {
        'teleconsulta': teleconsulta,
        'form': form
    })

#View para emissão de receitas
@role_required('medico')
def emitir_receita_consulta(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk, medico=request.user)
    paciente = consulta.paciente

    if request.method == 'POST':
        form = ReceitaForm(request.POST)
        if form.is_valid():
            receita = form.save(commit=False)
            receita.consulta = consulta
            receita.medico = request.user
            receita.paciente = paciente
            receita.save()

            html = render_to_string('consultas/receita_pdf.html', {'receita': receita})
            resultado = io.BytesIO()
            pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=resultado)
            receita.arquivo_pdf.save(f'receita_{receita.id}.pdf', ContentFile(resultado.getvalue()))
            receita.save()

            return redirect('detalhar_consulta', pk=consulta.pk)
    else:
        form = ReceitaForm()

    return render(request, 'consultas/form_receita_consulta.html', {
        'consulta': consulta,
        'form': form
    })


@role_required('medico')
def emitir_receita_teleconsulta(request, pk):
    teleconsulta = get_object_or_404(Teleconsulta, pk=pk, medico=request.user)
    paciente = teleconsulta.paciente

    if request.method == 'POST':
        form = ReceitaForm(request.POST)
        if form.is_valid():
            receita = form.save(commit=False)
            receita.teleconsulta = teleconsulta
            receita.medico = request.user
            receita.paciente = paciente
            receita.save()

            html = render_to_string('consultas/receita_pdf.html', {'receita': receita})
            resultado = io.BytesIO()
            pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=resultado)
            receita.arquivo_pdf.save(f'receita_{receita.id}.pdf', ContentFile(resultado.getvalue()))
            receita.save()

            return redirect('detalhar_teleconsulta', pk=teleconsulta.pk)
    else:
        form = ReceitaForm()

    return render(request, 'consultas/form_receita_teleconsulta.html', {
        'teleconsulta': teleconsulta,
        'form': form
    })

#View para emissão de atestados
@role_required('medico')
def emitir_atestado_consulta(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk, medico=request.user)
    paciente = consulta.paciente

    if request.method == 'POST':
        form = AtestadoForm(request.POST)
        if form.is_valid():
            atestado = form.save(commit=False)
            atestado.consulta = consulta
            atestado.medico = request.user
            atestado.paciente = paciente
            atestado.save()

            html = render_to_string('consultas/atestado_pdf.html', {'atestado': atestado})
            resultado = io.BytesIO()
            pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=resultado)
            atestado.arquivo_pdf.save(f'atestado_{atestado.id}.pdf', ContentFile(resultado.getvalue()))
            atestado.save()

            return redirect('detalhar_consulta', pk=consulta.pk)
    else:
        form = AtestadoForm()

    return render(request, 'consultas/form_atestado_consulta.html', {
        'consulta': consulta,
        'form': form
    })


@role_required('medico')
def emitir_atestado_teleconsulta(request, pk):
    teleconsulta = get_object_or_404(Teleconsulta, pk=pk, medico=request.user)
    paciente = teleconsulta.paciente

    if request.method == 'POST':
        form = AtestadoForm(request.POST)
        if form.is_valid():
            atestado = form.save(commit=False)
            atestado.teleconsulta = teleconsulta
            atestado.medico = request.user
            atestado.paciente = paciente
            atestado.save()

            html = render_to_string('consultas/atestado_pdf.html', {'atestado': atestado})
            resultado = io.BytesIO()
            pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=resultado)
            atestado.arquivo_pdf.save(f'atestado_{atestado.id}.pdf', ContentFile(resultado.getvalue()))
            atestado.save()

            return redirect('detalhar_teleconsulta', pk=teleconsulta.pk)
    else:
        form = AtestadoForm()

    return render(request, 'consultas/form_atestado_teleconsulta.html', {
        'teleconsulta': teleconsulta,
        'form': form
    })

#View de visualização de laudo
@role_required('medico', 'paciente', 'administrativo')
def visualizar_laudo(request, laudo_id):
    laudo = get_object_or_404(Laudo, id=laudo_id)

    # Verifica se o usuário tem permissão para visualizar
    if request.user != laudo.medico and request.user != laudo.paciente and request.user.role != 'administrativo':
        return HttpResponseForbidden("Você não tem permissão para acessar este laudo.")

    # Retorna o PDF se disponível
    if laudo.arquivo_pdf:
        return FileResponse(laudo.arquivo_pdf.open('rb'), content_type='application/pdf')

    return HttpResponse("Arquivo não encontrado.", status=404)

#view para visualizar atestado
@role_required('medico', 'paciente', 'administrativo')
def visualizar_atestado(request, atestado_id):
    atestado = get_object_or_404(Atestado, id=atestado_id)

    if request.user != atestado.medico and request.user != atestado.paciente and request.user.role != 'administrativo':
        return HttpResponseForbidden("Você não tem permissão para acessar este atestado.")

    if atestado.arquivo_pdf:
        return FileResponse(atestado.arquivo_pdf.open('rb'), content_type='application/pdf')
    return HttpResponse("Arquivo não encontrado.", status=404)


#View de visualização de receitas
@role_required('medico', 'paciente', 'administrativo')
def visualizar_receita(request, receita_id):
    receita = get_object_or_404(Receita, id=receita_id)

    if request.user != receita.medico and request.user != receita.paciente and request.user.role != 'administrativo':
        return HttpResponseForbidden("Você não tem permissão para acessar esta receita.")

    if receita.arquivo_pdf:
        return FileResponse(receita.arquivo_pdf.open('rb'), content_type='application/pdf')
    return HttpResponse("Arquivo não encontrado.", status=404)

#View para a visualização do prontuario
@role_required('medico')
def visualizar_prontuario(request, paciente_id):
    paciente = get_object_or_404(Usuario, id=paciente_id, role='paciente')
    prontuario, created = Prontuario.objects.get_or_create(paciente=paciente)

    if request.method == 'POST':
        form = ProntuarioForm(request.POST, instance=prontuario)
        if form.is_valid():
            form.save()
            messages.success(request, 'Prontuário atualizado com sucesso.')
            return redirect('visualizar_prontuario', paciente_id=paciente.id)
    else:
        form = ProntuarioForm(instance=prontuario)

    consultas = Consulta.objects.filter(paciente=paciente, status='finalizada')
    exames = Exame.objects.filter(paciente=paciente, status='finalizado')
    teleconsultas = Teleconsulta.objects.filter(paciente=paciente, status='finalizada')

    return render(request, 'consultas/prontuario.html', {
        'paciente': paciente,
        'form': form,
        'consultas': consultas,
        'exames': exames,
        'teleconsultas': teleconsultas
    })

# View para seleção de paciente antes de abrir o prontuário quando fora de consulta
def selecionar_paciente_prontuario(request):
    if request.method == 'POST':
        form = SelecionarPacienteForm(request.POST)
        if form.is_valid():
            paciente = form.cleaned_data['paciente']
            return redirect('visualizar_prontuario', paciente_id=paciente.id)
    else:
        form = SelecionarPacienteForm()

    return render(request, 'consultas/selecionar_paciente.html', {'form': form})

#View separada para paciente e administrativo, para evitar problemas com funções exclusivas de medico
@role_required('paciente', 'administrativo')
def consultas_usuario(request):
    usuario = request.user
    if usuario.role == 'paciente':
        consultas = Consulta.objects.filter(paciente=usuario).order_by('-agenda__data')
    elif usuario.role == 'administrativo':
        consultas = Consulta.objects.all().order_by('-agenda__data')
    return render(request, 'consultas/consultas_usuario.html', {'consultas': consultas})

@role_required('paciente', 'administrativo')
def exames_usuario(request):
    usuario = request.user
    if usuario.role == 'paciente':
        exames = Exame.objects.filter(paciente=usuario).order_by('-agenda__data')
    else:
        exames = Exame.objects.all().order_by('-agenda__data')
    return render(request, 'exames/exames_usuario.html', {'exames': exames})

@role_required('paciente', 'administrativo')
def teleconsultas_usuario(request):
    usuario = request.user
    if usuario.role == 'paciente':
        teleconsultas = Teleconsulta.objects.filter(paciente=usuario).order_by('-agenda__data')
    else:
        teleconsultas = Teleconsulta.objects.all().order_by('-agenda__data')
    return render(request, 'teleconsultas/teleconsultas_usuario.html', {'teleconsultas': teleconsultas})

#View para consultas de consultas
@role_required('paciente', 'administrativo')
def detalhar_consulta_usuario(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)
    if request.user.role == 'paciente' and consulta.paciente != request.user:
        return render(request, '403.html', status=403)
    return render(request, 'consultas/detalhar_consulta_usuario.html', {'consulta': consulta})

#Para a criação de pagina para exibir o redirecionamento em caso de acesso a pagina sem acesso
def erro_403(request, exception=None):
    return render(request, '403.html', status=403)

#View adicionada para permitir o dinamismo na consulta de horarios livres de exames
@role_required('administrativo', 'paciente')
def agendas_disponiveis_exame(request):
    tipo = request.GET.get('tipo')
    if not tipo:
        return JsonResponse({'agendas': []})

    agendas = AgendaExame.objects.filter(tipo_exame=tipo, status_manual='livre').order_by('data', 'horario_inicio')
    agendas = [a for a in agendas if a.esta_disponivel]

    agendas_data = [
        {
            'id': a.id,
            'descricao': f"{a.data.strftime('%d/%m/%Y')} - {a.horario_inicio.strftime('%H:%M')} ({a.sala})"
        }
        for a in agendas
    ]

    return JsonResponse({'agendas': agendas_data})

#iniciar e alterar teleconsultas
@role_required('medico')
def iniciar_teleconsulta(request, pk):
    tele = get_object_or_404(Teleconsulta, pk=pk, medico=request.user)

    if tele.status != 'agendada':
        messages.error(request, 'Esta teleconsulta não pode ser iniciada.')
        return redirect('lista_teleconsultas')

    tele.status = 'em_andamento'
    tele.save()

    return redirect('detalhar_teleconsulta', pk=tele.id)

@role_required('medico')
def cancelar_atendimento_teleconsulta(request, pk):
    tele = get_object_or_404(Teleconsulta, pk=pk, medico=request.user)

    if request.method == 'POST' and tele.status == 'em_andamento':
        tele.status = 'agendada'
        tele.save()
        messages.success(request, 'Atendimento cancelado com sucesso.')
    return redirect('lista_teleconsultas')

@role_required('medico')
def encerrar_atendimento_teleconsulta(request, pk):
    tele = get_object_or_404(Teleconsulta, pk=pk, medico=request.user)

    if request.method == 'POST' and tele.status == 'em_andamento':
        tele.status = 'finalizada'
        tele.save()
        messages.success(request, 'Atendimento finalizado com sucesso.')
    return redirect('lista_teleconsultas')

@role_required('medico')
def detalhar_teleconsulta(request, pk):
    teleconsulta = get_object_or_404(Teleconsulta, pk=pk, medico=request.user)

    if request.method == 'POST':
        form = ObservacoesConsultaForm(request.POST, instance=teleconsulta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Observações atualizadas com sucesso.')
            return redirect('detalhar_teleconsulta', pk=pk)
    else:
        form = ObservacoesConsultaForm(instance=teleconsulta)

    return render(request, 'teleconsultas/detalhar_teleconsulta.html', {
        'teleconsulta': teleconsulta,
        'form_observacoes': form,
    })

#view para detalhar informações do exame para tratamento pelo medico
@role_required('medico')
def detalhar_exame(request, pk):
    exame = get_object_or_404(Exame, pk=pk, medico=request.user)

    if request.method == 'POST':
        form = ObservacoesConsultaForm(request.POST, instance=exame)
        if form.is_valid():
            form.save()
            messages.success(request, 'Observações atualizadas com sucesso.')
            return redirect('detalhar_exame', pk=pk)
    else:
        form = ObservacoesConsultaForm(instance=exame)

    return render(request, 'exames/detalhar_exame.html', {
        'exame': exame,
        'form_observacoes': form
    })

#view para emissão de documentos de exame
@role_required('medico')
def emitir_resultado_exame(request, pk):
    exame = get_object_or_404(Exame, pk=pk, medico=request.user)
    paciente = exame.paciente

    if request.method == 'POST':
        form = ResultadoExameForm(request.POST, request.FILES)
        if form.is_valid():
            resultado = form.save(commit=False)
            resultado.exame = exame
            resultado.medico = request.user
            resultado.paciente = paciente
            resultado.save()

            html = render_to_string('exames/resultado_exame_pdf.html', {'resultado': resultado})
            resultado_io = io.BytesIO()
            pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=resultado_io)
            resultado.arquivo_pdf.save(f'resultado_exame_{resultado.id}.pdf', ContentFile(resultado_io.getvalue()))
            resultado.save()

            return redirect('detalhar_exame', pk=exame.pk)
    else:
        form = ResultadoExameForm()

    return render(request, 'exames/form_resultado_exame.html', {
        'exame': exame,
        'form': form
    })

#view para visualizar o resultado exame
@role_required('medico', 'paciente', 'administrativo')
def visualizar_resultado_exame(request, resultado_id):
    resultado = get_object_or_404(ResultadoExame, id=resultado_id)

    if request.user != resultado.medico and request.user != resultado.paciente and request.user.role != 'administrativo':
        return HttpResponseForbidden("Você não tem permissão para acessar este resultado.")

    if resultado.arquivo_pdf:
        return FileResponse(resultado.arquivo_pdf.open('rb'), content_type='application/pdf')

    return HttpResponse("Arquivo não encontrado.", status=404)

#view para cancelar o atendimento
@role_required('medico')
def cancelar_atendimento_exame(request, pk):
    exame = get_object_or_404(Exame, pk=pk, medico=request.user)

    if request.method == 'POST' and exame.status == 'em_andamento':
        exame.status = 'agendada'
        exame.save()
        messages.success(request, 'Atendimento cancelado. Exame voltou ao status "agendado".')

    return redirect('lista_exames')

#view para finalizar o atendimento
@role_required('medico')
def encerrar_atendimento_exame(request, pk):
    exame = get_object_or_404(Exame, pk=pk, medico=request.user)

    if request.method == 'POST' and exame.status == 'em_andamento':
        exame.status = 'finalizada'
        exame.save()
        messages.success(request, 'Exame finalizado com sucesso.')

    return redirect('lista_exames')

#view para listar exames
@role_required('medico')
def lista_exames(request):
    exames = Exame.objects.all().order_by('-agenda__data', '-agenda__horario_inicio')
    return render(request, 'exames/lista_exames.html', {
        'exames': exames,
        'medico_logado': request.user
    })

#view para iniciar o atendimento
@role_required('medico')
def iniciar_atendimento_exame(request, pk):
    exame = get_object_or_404(Exame, pk=pk)

    if exame.status != 'agendada':
        messages.error(request, 'Este exame não pode ser iniciado.')
        return redirect('lista_exames')

    # Se já tem médico atribuído diferente do atual
    if exame.medico and exame.medico != request.user:
        if request.method == 'POST' and 'confirmar' in request.POST:
            exame.medico = request.user
            exame.status = 'em_andamento'
            exame.save()
            return redirect('detalhar_exame', pk=exame.pk)
        return render(request, 'exames/confirmar_substituicao.html', {
            'exame': exame,
            'medico_atual': exame.medico
        })

    # Se não tem médico ou já é o médico certo
    exame.medico = request.user
    exame.status = 'em_andamento'
    exame.save()
    return redirect('detalhar_exame', pk=exame.pk)

#View para a teleconsulta por pacientes e administrativo
@role_required('paciente', 'administrativo')
def detalhar_teleconsulta_usuario(request, pk):
    teleconsulta = get_object_or_404(Teleconsulta, pk=pk)

    # Paciente só pode acessar se for o próprio atendimento
    if request.user.role == 'paciente' and teleconsulta.paciente != request.user:
        return render(request, '403.html', status=403)

    # Variável de controle para exibição de observações internas
    mostrar_obs_internas = request.user.role == 'administrativo'

    return render(request, 'teleconsultas/detalhar_teleconsulta_usuario.html', {
        'teleconsulta': teleconsulta,
        'mostrar_obs_internas': mostrar_obs_internas,
    })

#view para detalhamento de exames
@role_required('paciente', 'administrativo')
def detalhar_exame_usuario(request, pk):
    exame = get_object_or_404(Exame, pk=pk)

    # Paciente só pode acessar se for o próprio exame
    if request.user.role == 'paciente' and exame.paciente != request.user:
        return render(request, '403.html', status=403)

    mostrar_obs_internas = request.user.role == 'administrativo'

    return render(request, 'exames/detalhar_exame_usuario.html', {
        'exame': exame,
        'mostrar_obs_internas': mostrar_obs_internas,
    })

