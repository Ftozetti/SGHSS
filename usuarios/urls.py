from django.urls import path
from . import views

urlpatterns = [
    # Página inicial e redirecionamento por perfil
    path('api/teste-login/', views.login_postman, name='login_postman'),
    path('api/token-login/', views.api_login_token, name='token_login'),

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
    path('consultas/<int:pk>/emitir-laudo/', views.emitir_laudo_consulta, name='emitir_laudo_consulta'),
    path('consultas/<int:pk>/emitir-atestado/', views.emitir_atestado_consulta, name='emitir_atestado_consulta'),
    path('consultas/<int:pk>/emitir-receita/', views.emitir_receita_consulta, name='emitir_receita_consulta'),
    path('consultas/usuario/', views.consultas_usuario, name='consultas_usuario'),
    path('consultas/usuario/<int:pk>/detalhar/', views.detalhar_consulta_usuario, name='detalhar_consulta_usuario'),
    path('consultas/cancelar/<int:consulta_id>/', views.cancelar_consulta, name='cancelar_consulta'),
    path('consultas/administrativo/<int:pk>/detalhar/', views.detalhar_consulta_usuario, name='detalhar_consulta_admin'),


    # Exames
    path('exames/agendar/', views.agendar_exame, name='agendar_exame'),
    path('exames/usuario/', views.exames_usuario, name='exames_usuario'),
    path('ajax/agendas-disponiveis-exame/', views.agendas_disponiveis_exame, name='ajax_agendas_exame'),
    path('exames/<int:exame_id>/cancelar/', views.cancelar_exame, name='cancelar_exame'),
    path('exames/<int:pk>/emitir-resultado/', views.emitir_resultado_exame, name='emitir_resultado_exame'),
    path('exames/<int:pk>/detalhar/', views.detalhar_exame, name='detalhar_exame'),
    path('exames/<int:pk>/cancelar-atendimento/', views.cancelar_atendimento_exame, name='cancelar_atendimento_exame'),
    path('exames/<int:pk>/encerrar/', views.encerrar_atendimento_exame, name='encerrar_atendimento_exame'),
    path('exames/medico/', views.lista_exames, name='lista_exames'),
    path('documentos/resultado-exame/<int:resultado_id>/', views.visualizar_resultado_exame, name='visualizar_resultado_exame'),
    path('exames/<int:pk>/iniciar/', views.iniciar_atendimento_exame, name='iniciar_atendimento_exame'),
    path('exames/<int:pk>/detalhar/', views.detalhar_exame_usuario, name='detalhar_exame_usuario'),
    path('exames/administrativo/<int:pk>/detalhar/', views.detalhar_exame_usuario, name='detalhar_exame_admin'),

    # Teleconsultas
    path('teleconsultas/agendar/', views.agendar_teleconsulta, name='agendar_teleconsulta'),
    path('teleconsultas/usuario/', views.teleconsultas_usuario, name='teleconsultas_usuario'),
    path('teleconsultas/<int:teleconsulta_id>/cancelar/', views.cancelar_teleconsulta, name='cancelar_teleconsulta'),
    path('teleconsultas/<int:pk>/emitir-laudo/', views.emitir_laudo_teleconsulta, name='emitir_laudo_teleconsulta'),
    path('teleconsultas/<int:pk>/emitir-atestado/', views.emitir_atestado_teleconsulta, name='emitir_atestado_teleconsulta'),
    path('teleconsultas/<int:pk>/emitir-receita/', views.emitir_receita_teleconsulta, name='emitir_receita_teleconsulta'),
    path('teleconsultas/medico/', views.lista_teleconsultas, name='lista_teleconsultas'),
    path('teleconsultas/<int:pk>/detalhar/', views.detalhar_teleconsulta, name='detalhar_teleconsulta'),
    path('teleconsultas/<int:pk>/iniciar/', views.iniciar_teleconsulta, name='iniciar_teleconsulta'),
    path('teleconsultas/<int:pk>/cancelar-atendimento/', views.cancelar_atendimento_teleconsulta, name='cancelar_atendimento_teleconsulta'),
    path('teleconsultas/<int:pk>/encerrar/', views.encerrar_atendimento_teleconsulta, name='encerrar_atendimento_teleconsulta'),
    path('teleconsultas/<int:pk>/detalhar/', views.detalhar_teleconsulta_usuario, name='detalhar_teleconsulta_usuario'),
    path('teleconsultas/administrativo/<int:pk>/detalhar/', views.detalhar_teleconsulta_usuario, name='detalhar_teleconsulta_admin'),


    # Prontuário
    path('prontuario/<int:paciente_id>/', views.visualizar_prontuario, name='visualizar_prontuario'),
    path('prontuario/selecionar/', views.selecionar_paciente_prontuario, name='selecionar_paciente_prontuario'),

    # Documentos médicos (PDFs)
    path('documentos/laudo/<int:laudo_id>/', views.visualizar_laudo, name='visualizar_laudo'),
    path('documentos/receita/<int:receita_id>/', views.visualizar_receita, name='visualizar_receita'),
    path('documentos/atestado/<int:atestado_id>/', views.visualizar_atestado, name='visualizar_atestado'),

    #Financeiro
    path('financeiro/receitas/', views.relatorio_receitas, name='relatorio_receitas'),
    path('financeiro/pagamentos/materiais/', views.relatorio_pagamentos_materiais, name='relatorio_pagamentos_materiais'),


    #materiais
    path('estoque/', views.visualizar_estoque, name='visualizar_estoque'),
    path('materiais/novo/', views.criar_pedido_material, name='criar_pedido_material'),
    path('materiais/financeiro/<int:pedido_id>/aprovar/', views.aprovar_pedido_material, name='aprovar_pedido_material'),
    path('materiais/financeiro/', views.listar_pedidos_financeiro, name='listar_pedidos_financeiro'),
    path('materiais/', views.listar_pedidos_administrativo, name='listar_pedidos_administrativo'),
    path('materiais/<int:pedido_id>/confirmar-entrega/', views.confirmar_entrega_pedido, name='confirmar_entrega_pedido'),

    #cadastro de pacientes
    path('cadastrar-paciente/', views.cadastrar_paciente_view, name='cadastrar_paciente'),
    path('pacientes/', views.listar_pacientes_view, name='listar_pacientes'),







]
