from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# View de login
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Verifica o tipo de usuário e redireciona para a página correspondente
            user_profile = user.profile  # Acessa o perfil do usuário
            
            if user_profile.role in [1, 2]:  # Diretor ou Administrativo
                return redirect('painel_de_controle')  # Redireciona para a página 'criar_ordem_servico'
            elif user_profile.role == 3:  # Líder Técnico
                return redirect('servicos')  # Redireciona para a página 'lider_tecnico'
            elif user_profile.role in [4, 5]:  # Sub-Líder Técnico ou Técnico
                return redirect('tarefas')  # Redireciona para a página 'tecnico'
        
        else:
           messages.error(request, "Usuário ou senha inválidos!")
    
    return render(request, 'ordemServico/Login.html')

# View de logout
def user_logout(request):
    logout(request)
    return redirect('login')  # Redireciona para a página de login após o logout
