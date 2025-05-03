from django.urls import path
from . import views

urlpatterns = [
    path('', views.redirecionar_dashboard, name='home'),
    path('redirecionar/', views.redirecionar_dashboard, name='redirecionar_dashboard'),
    path('dashboard/paciente/', views.dashboard_paciente, name='dashboard_paciente'),
    path('dashboard/medico/', views.dashboard_medico, name='dashboard_medico'),
    path('dashboard/administrativo/', views.dashboard_administrativo, name='dashboard_administrativo'),
    path('dashboard/financeiro/', views.dashboard_financeiro, name='dashboard_financeiro'),
    path('estrutura/', views.lista_salas, name='lista_salas'),
    path('estrutura/adicionar/', views.adicionar_sala, name='adicionar_sala'),
    path('estrutura/<int:pk>/editar/', views.editar_sala, name='editar_sala'),
    path('estrutura/<int:pk>/excluir/', views.excluir_sala, name='excluir_sala'),
    path('agenda/', views.lista_agenda, name='lista_agenda'),
    path('agenda/nova/', views.criar_agenda, name='criar_agenda'),
    path('agenda/<int:pk>/editar/', views.editar_agenda, name='editar_agenda'),
    path('agenda/<int:pk>/excluir/', views.excluir_agenda, name='excluir_agenda'),
    path('consultas/', views.lista_consultas, name='lista_consultas'),
    path('consultas/agendar/', views.agendar_consulta, name='agendar_consulta'),
]