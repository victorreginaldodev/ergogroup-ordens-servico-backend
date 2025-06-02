from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from ordemServico.forms import RepositorioForm
from ordemServico.models import Profile

# Função que verifica se o usuário é 'Diretor', 'Administrativo' ou 'Líder Técnico'
def verificar_tipo_usuario(user):
    try:
        return user.profile.role in [1, 2, 3]
    except Profile.DoesNotExist:
        return False


@login_required
@user_passes_test(verificar_tipo_usuario)
def repositorio(request):
    if request.method == 'POST':
        form = RepositorioForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('repositorio') 
    else:
        form = RepositorioForm()  

    return render(request, 'ordemServico/repositorio.html', {'form': form})