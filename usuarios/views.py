from datetime import timedelta, datetime
from django.utils import timezone
from django.utils.timezone import make_aware
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import (Sala, Agenda, Consulta, Usuario, Prontuario, Exame, Teleconsulta, Laudo, 
                     Receita, Atestado
)
from .forms import (SalaForm, AgendaForm, ConsultaForm, 
                    CancelamentoConsultaForm, LaudoForm, ReceitaForm, AtestadoForm, ProntuarioForm,
                    ObservacoesConsultaForm, SelecionarPacienteForm                    
)
from .decorators import role_required
from django import forms
from django.template.loader import render_to_string
from django.http import HttpResponse, FileResponse, HttpResponseForbidden
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

@role_required('administrativo')
def lista_agenda(request):
    agendas = Agenda.objects.order_by('data', 'horario_inicio')
    
    # Adiciona flag para saber se pode editar ou não
    for a in agendas:
        a.tem_consulta_ativa = a.consultas.exclude(status='cancelada').exists()

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

    # Impede edição se houver consulta vinculada que não esteja cancelada
    if agenda.consultas.exclude(status='cancelada').exists():
        messages.error(request, 'Não é possível editar um horário com consultas em andamento, agendadas ou finalizadas.')
        return redirect('lista_agenda')

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
    if agenda.consultas.exists():
        messages.error(request, 'Não é possível excluir um horário com consulta agendada. Cancele antes.')
        return redirect('lista_agenda')

    if request.method == 'POST':
        agenda.delete()
        return redirect('lista_agenda')

    return render(request, 'agenda/excluir_agenda.html', {'agenda': agenda})

#Bloqueio manual de Agenda
@role_required('administrativo')
def bloquear_agenda(request, pk):
    agenda = get_object_or_404(Agenda, pk=pk)
    agenda.status_manual = 'bloqueado'
    agenda.save()
    messages.success(request, 'Horário bloqueado com sucesso.')
    return redirect('lista_agenda')

#Desbloqueio Manual de agenda
@role_required('administrativo')
def desbloquear_agenda(request, pk):
    agenda = get_object_or_404(Agenda, pk=pk)

    if agenda.consultas.filter(status='agendada').exists():
        messages.error(request, 'Não é possível desbloquear um horário com consulta agendada.')
        return redirect('lista_agenda')

    agenda.status_manual = 'livre'
    agenda.save()
    messages.success(request, 'Horário desbloqueado com sucesso.')
    return redirect('lista_agenda')

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
            if agenda.procedimento != 'consulta' or agenda.consultas.exclude(status='cancelada').exists():
                messages.error(request, 'Horário indisponível.')
                return redirect('agendar_consulta')


            # Verifica se o médico do agendamento bate com o da agenda
            if consulta.medico != agenda.medico:
                messages.error(request, 'O médico selecionado não atende neste horário.')
                return redirect('agendar_consulta')

            # Verifica se o paciente já tem outro procedimento no mesmo horário
            conflito = Consulta.objects.filter(
                paciente=consulta.paciente,
                agenda=agenda
            ).exclude(status='cancelada').exists()
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
@role_required('medico')
def lista_consultas(request):
    consultas = Consulta.objects.filter(medico=request.user).order_by('-agenda__data')
    return render(request, 'consultas/lista_consultas.html', {'consultas': consultas})

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



#View para iniciar consulta
@role_required('medico')
def iniciar_consulta(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk, medico=request.user)
    
    if consulta.status != 'agendada':
        messages.error(request, 'A consulta não pode ser iniciada.')
        return redirect('lista_consultas')

    consulta.status = 'em atendimento'
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
        'form_observacoes': form
    })

#View que permite o cancelamento do atendimento e retorna o status para agendado
@role_required('medico')
def cancelar_atendimento(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk, medico=request.user)
    if request.method == 'POST' and consulta.status == 'em atendimento':
        consulta.status = 'agendada'
        consulta.save()
    return redirect('lista_consultas')

# view que encerra o atendimento e altera o status para finalizada
@role_required('medico')
def encerrar_atendimento(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk, medico=request.user)
    if request.method == 'POST' and consulta.status == 'em atendimento':
        consulta.status = 'finalizada'
        consulta.save()
    return redirect('lista_consultas') 

#View para emissão de laudo em pdf
@role_required('medico')
def emitir_laudo(request, pk):
    consulta = get_object_or_404(Consulta, id=pk)

    if request.method == 'POST':
        form = LaudoForm(request.POST)
        if form.is_valid():
            laudo = form.save(commit=False)
            laudo.consulta = consulta
            laudo.medico = request.user
            laudo.paciente = consulta.paciente
            laudo.save()

            html = render_to_string('consultas/laudo_pdf.html', {'laudo': laudo})
            resultado = io.BytesIO()
            pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=resultado)

            laudo.arquivo_pdf.save(f'laudo_{laudo.id}.pdf', ContentFile(resultado.getvalue()))
            laudo.save()

            return redirect('detalhar_consulta', pk=consulta.id)
    else:
        form = LaudoForm()

    return render(request, 'consultas/form_laudo.html', {'consulta': consulta, 'form': form})

#View para visualizar laudo
@role_required('medico', 'paciente', 'administrativo')
def visualizar_laudo(request, laudo_id):
    laudo = get_object_or_404(Laudo, id=laudo_id)

    # Verifica se o usuário tem permissão
    if request.user != laudo.medico and request.user != laudo.paciente and request.user.role != 'administrativo':
        return HttpResponseForbidden("Você não tem permissão para acessar este laudo.")

    if laudo.arquivo_pdf:
        return FileResponse(laudo.arquivo_pdf.open('rb'), content_type='application/pdf')
    return HttpResponse("Arquivo não encontrado.", status=404)


#View para emissão de atestados
@role_required('medico')
def emitir_atestado(request, pk):
    consulta = get_object_or_404(Consulta, id=pk)

    if request.method == 'POST':
        form = AtestadoForm(request.POST)
        if form.is_valid():
            atestado = form.save(commit=False)
            atestado.consulta = consulta
            atestado.medico = request.user
            atestado.paciente = consulta.paciente
            atestado.save()

        html = render_to_string('consultas/atestado_pdf.html', {'atestado': atestado})
        resultado = io.BytesIO()
        pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=resultado)

        atestado.arquivo_pdf.save(f'atestado_{atestado.id}.pdf', ContentFile(resultado.getvalue()))
        atestado.save()

        return redirect('detalhar_consulta', pk=consulta.id)
    
    else:
        form = AtestadoForm()

    return render(request, 'consultas/form_atestado.html', {'consulta': consulta, 'form': form})

#view para visualizar atestado
@role_required('medico', 'paciente', 'administrativo')
def visualizar_atestado(request, atestado_id):
    atestado = get_object_or_404(Atestado, id=atestado_id)

    if request.user != atestado.medico and request.user != atestado.paciente and request.user.role != 'administrativo':
        return HttpResponseForbidden("Você não tem permissão para acessar este atestado.")

    if atestado.arquivo_pdf:
        return FileResponse(atestado.arquivo_pdf.open('rb'), content_type='application/pdf')
    return HttpResponse("Arquivo não encontrado.", status=404)

#View para a emissão de receitas
@role_required('medico')
def emitir_receita(request, pk):
    consulta = get_object_or_404(Consulta, id=pk)

    if request.method == 'POST':
        form = ReceitaForm(request.POST)
        if form.is_valid():
            receita = form.save(commit=False)
            receita.consulta = consulta
            receita.medico = request.user
            receita.paciente = consulta.paciente
            receita.save()

            html = render_to_string('consultas/receita_pdf.html', {'receita': receita})
            resultado = io.BytesIO()
            pisa.CreatePDF(io.BytesIO(html.encode('utf-8')), dest=resultado)

            receita.arquivo_pdf.save(f'receita_{receita.id}.pdf', ContentFile(resultado.getvalue()))
            receita.save()

            return redirect('detalhar_consulta', pk=consulta.id)
    else:
        form = ReceitaForm()

    return render(request, 'consultas/form_receita.html', {'consulta': consulta, 'form': form})


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

#View para consultas de consultas, :O
@role_required('paciente', 'administrativo')
def detalhar_consulta_usuario(request, pk):
    consulta = get_object_or_404(Consulta, pk=pk)
    if request.user.role == 'paciente' and consulta.paciente != request.user:
        return render(request, '403.html', status=403)
    return render(request, 'consultas/detalhar_consulta_usuario.html', {'consulta': consulta})

