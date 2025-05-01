from django.urls import path
from .views import (
    redirecionar_dashboard,
    dashboard_paciente, dashboard_medico,
    dashboard_administrativo, dashboard_financeiro
)

urlpatterns = [
    path('', redirecionar_dashboard, name='home'),
    path('redirecionar/', redirecionar_dashboard, name='redirecionar_dashboard'),
    path('dashboard/paciente/', dashboard_paciente, name='dashboard_paciente'),
    path('dashboard/medico/', dashboard_medico, name='dashboard_medico'),
    path('dashboard/administrativo/', dashboard_administrativo, name='dashboard_administrativo'),
    path('dashboard/financeiro/', dashboard_financeiro, name='dashboard_financeiro'),
]