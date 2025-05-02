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
]