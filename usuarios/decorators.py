from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied

def role_required(*roles):
    """
    Decorador que permite o acesso apenas a usuários autenticados com um dos papéis especificados.
    Exemplo:
        @role_required('administrativo', 'financeiro')
    """
    def check_role(user):
        if user.is_authenticated and user.role in roles:
            return True
        raise PermissionDenied
    return user_passes_test(check_role)

