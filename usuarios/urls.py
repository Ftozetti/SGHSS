from django.urls import path
from . import views

urlpatterns = [
    # Página inicial e redirecionamento por perfil
    path('', views.redirecionar_dashboard, name='home'),
    path('redirecionar/', views.redirecionar_dashboard, name='redirecionar_dashboard'),

    # Dashboards por perfil
    path('dashboard/paciente/', views.dashboard_paciente, name='dashboard_paciente'),
    path('dashboard/medico/', views.dashboard_medico, name='dashboard_medico'),
    path('dashboard/administrativo/', views.dashboard_administrativo, name='dashboard_administrativo'),
    path('dashboard/financeiro/', views.dashboard_financeiro, name='dashboard_financeiro'),

    # Estrutura física (salas)
    path('estrutura/', views.lista_salas, name='lista_salas'),
    path('estrutura/adicionar/', views.adicionar_sala, name='adicionar_sala'),
    path('estrutura/<int:pk>/editar/', views.editar_sala, name='editar_sala'),
    path('estrutura/<int:pk>/excluir/', views.excluir_sala, name='excluir_sala'),

    # Agenda de Consultas
    path('agenda/consultas/', views.lista_agenda_consulta, name='lista_agenda_consulta'),
    path('agenda/consultas/nova/', views.criar_agenda_consulta, name='criar_agenda_consulta'),
    path('agenda/consultas/<int:pk>/editar/', views.editar_agenda_consulta, name='editar_agenda_consulta'),
    path('agenda/consultas/<int:pk>/excluir/', views.excluir_agenda_consulta, name='excluir_agenda_consulta'),
    path('agenda/consultas/<int:pk>/bloquear/', views.bloquear_agenda_consulta, name='bloquear_agenda_consulta'),
    path('agenda/consultas/<int:pk>/desbloquear/', views.desbloquear_agenda_consulta, name='desbloquear_agenda_consulta'),

    # Agenda de Exames
    path('agenda/exames/', views.lista_agenda_exame, name='lista_agenda_exame'),
    path('agenda/exames/nova/', views.criar_agenda_exame, name='criar_agenda_exame'),
    path('agenda/exames/<int:pk>/editar/', views.editar_agenda_exame, name='editar_agenda_exame'),
    path('agenda/exames/<int:pk>/excluir/', views.excluir_agenda_exame, name='excluir_agenda_exame'),
    path('agenda/exames/<int:pk>/bloquear/', views.bloquear_agenda_exame, name='bloquear_agenda_exame'),
    path('agenda/exames/<int:pk>/desbloquear/', views.desbloquear_agenda_exame, name='desbloquear_agenda_exame'),

    # Agenda de Teleconsultas
    path('agenda/teleconsultas/', views.lista_agenda_teleconsulta, name='lista_agenda_teleconsulta'),
    path('agenda/teleconsultas/nova/', views.criar_agenda_teleconsulta, name='criar_agenda_teleconsulta'),
    path('agenda/teleconsultas/<int:pk>/editar/', views.editar_agenda_teleconsulta, name='editar_agenda_teleconsulta'),
    path('agenda/teleconsultas/<int:pk>/excluir/', views.excluir_agenda_teleconsulta, name='excluir_agenda_teleconsulta'),
    path('agenda/teleconsultas/<int:pk>/bloquear/', views.bloquear_agenda_teleconsulta, name='bloquear_agenda_teleconsulta'),
    path('agenda/teleconsultas/<int:pk>/desbloquear/', views.desbloquear_agenda_teleconsulta, name='desbloquear_agenda_teleconsulta'),

    # Consultas
    path('consultas/', views.lista_consultas, name='lista_consultas'),
    path('consultas/agendar/', views.agendar_consulta, name='agendar_consulta'),
    path('consultas/<int:pk>/iniciar/', views.iniciar_consulta, name='iniciar_consulta'),
    path('consultas/<int:pk>/detalhar/', views.detalhar_consulta, name='detalhar_consulta'),
    path('consultas/<int:pk>/encerrar/', views.encerrar_atendimento, name='encerrar_atendimento'),
    path('consultas/<int:pk>/cancelar-atendimento/', views.cancelar_atendimento, name='cancelar_atendimento'),
    path('consultas/<int:pk>/emitir-laudo/', views.emitir_laudo, name='emitir_laudo'),
    path('consultas/<int:pk>/emitir-atestado/', views.emitir_atestado, name='emitir_atestado'),
    path('consultas/<int:pk>/emitir-receita/', views.emitir_receita, name='emitir_receita'),
    path('consultas/usuario/', views.consultas_usuario, name='consultas_usuario'),
    path('consultas/usuario/<int:pk>/detalhar/', views.detalhar_consulta_usuario, name='detalhar_consulta_usuario'),
    path('consultas/cancelar/<int:consulta_id>/', views.cancelar_consulta, name='cancelar_consulta'),

    # Exames
    path('exames/agendar/', views.agendar_exame, name='agendar_exame'),
    path('exames/usuario/', views.exames_usuario, name='exames_usuario'),
    path('ajax/agendas-disponiveis-exame/', views.agendas_disponiveis_exame, name='ajax_agendas_exame'),
    path('exames/<int:exame_id>/cancelar/', views.cancelar_exame, name='cancelar_exame'),

    # Teleconsultas
    path('teleconsultas/agendar/', views.agendar_teleconsulta, name='agendar_teleconsulta'),
    path('teleconsultas/usuario/', views.teleconsultas_usuario, name='teleconsultas_usuario'),
    path('teleconsultas/<int:teleconsulta_id>/cancelar/', views.cancelar_teleconsulta, name='cancelar_teleconsulta'),
    path('teleconsultas/<int:pk>/emitir-laudo/', views.emitir_laudo, name='emitir_laudo'),
    path('teleconsultas/<int:pk>/emitir-atestado/', views.emitir_atestado, name='emitir_atestado'),
    path('teleconsultas/<int:pk>/emitir-receita/', views.emitir_receita, name='emitir_receita'),
    path('teleconsultas/medico/', views.lista_teleconsultas, name='lista_teleconsultas'),
    path('teleconsultas/<int:pk>/detalhar/', views.detalhar_teleconsulta, name='detalhar_teleconsulta'),
    path('teleconsultas/<int:pk>/iniciar/', views.iniciar_teleconsulta, name='iniciar_teleconsulta'),
    path('teleconsultas/<int:pk>/cancelar-atendimento/', views.cancelar_atendimento_teleconsulta, name='cancelar_atendimento_teleconsulta'),
    path('teleconsultas/<int:pk>/encerrar/', views.encerrar_atendimento_teleconsulta, name='encerrar_atendimento_teleconsulta'),


    

    # Prontuário
    path('prontuario/<int:paciente_id>/', views.visualizar_prontuario, name='visualizar_prontuario'),
    path('prontuario/selecionar/', views.selecionar_paciente_prontuario, name='selecionar_paciente_prontuario'),

    # Documentos médicos (PDFs)
    path('documentos/laudo/<int:laudo_id>/', views.visualizar_laudo, name='visualizar_laudo'),
    path('documentos/receita/<int:receita_id>/', views.visualizar_receita, name='visualizar_receita'),
    path('documentos/atestado/<int:atestado_id>/', views.visualizar_atestado, name='visualizar_atestado'),
]
