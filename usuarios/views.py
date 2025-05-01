from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

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

@login_required
def dashboard_paciente(request):
    return render(request, 'dashboard/paciente.html')

@login_required
def dashboard_medico(request):
    return render(request, 'dashboard/medico.html')

@login_required
def dashboard_administrativo(request):
    return render(request, 'dashboard/administrativo.html')

@login_required
def dashboard_financeiro(request):
    return render(request, 'dashboard/financeiro.html')


