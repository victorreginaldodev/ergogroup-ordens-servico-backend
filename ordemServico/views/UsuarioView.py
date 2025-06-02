from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from ordemServico.forms import UserUpdateForm  # Importa o formulário customizado

@login_required
def usuario(request):
    if request.method == 'POST':
        # Formulário de alteração de informações pessoais (e-mail) e senha
        user_form = UserUpdateForm(request.POST, instance=request.user)
        password_form = PasswordChangeForm(user=request.user, data=request.POST)

        if user_form.is_valid() and password_form.is_valid():
            user_form.save()  # Atualiza o e-mail
            user = password_form.save()  # Atualiza a senha
            update_session_auth_hash(request, user)  # Mantém o usuário logado após a troca de senha
            messages.success(request, 'As informações foram atualizadas com sucesso.')
            return redirect('usuario')
        else:
            messages.error(request, 'Por favor, corrija os erros no formulário.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(user=request.user)

    return render(request, 'ordemServico/usuario.html', {
        'user_form': user_form,
        'password_form': password_form,
    })
