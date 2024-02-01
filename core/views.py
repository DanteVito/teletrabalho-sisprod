from django.conf import settings
from django.http import HttpResponseForbidden
from django.views.static import serve


def secure_media(request, path):
    """
    View que garante que apenas superuser seja
    capaz de acessar os paths de download de arquivos
    de media.

    Poderíamos implementar um filtro para permitir que
    apenas o usuário que fez o upload seja capaz de fazer
    o download direto, mas do ponto de vista da segurança
    talvez seja melhor bloquear todos os downloads diretos
    e implantar o download de arquivo via response dos arquivos
    nas views em que esse download seja necessário.
    """
    if request.user.is_superuser:
        return serve(request, path, document_root=settings.MEDIA_ROOT)
    elif request.user.groups.filter(name='CIGT'):
        return serve(request, path, document_root=settings.MEDIA_ROOT)
    return HttpResponseForbidden()
