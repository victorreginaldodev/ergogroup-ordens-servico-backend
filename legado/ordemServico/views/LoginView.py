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
            
            user_profile = user.profile 
            
            if user_profile.role in [1, 2]: 
                return redirect('painel_de_controle') 
            elif user_profile.role in [3, 4]: 
                return redirect('lista_servicos') 
            elif user_profile.role in [4, 5]:
                return redirect('tarefas') 
        
        else:
           messages.error(request, "Usuário ou senha inválidos!")
    
    return render(request, 'ordemServico/Login.html')


# View de logout
def user_logout(request):
    logout(request)
    return redirect('login')
