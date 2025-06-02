from django.shortcuts import render, redirect
from django.contrib import messages
from ordemServico.forms import UserRegisterForm, ProfileRegisterForm

def register(request):
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileRegisterForm(request.POST, request.FILES)
        
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile = profile_form.save(commit=False)
            profile.user = user  # Associa o perfil ao usuário recém-criado
            profile.save()
            
            messages.success(request, 'Seu registro foi realizado com sucesso! Agora você pode fazer login.')
            return redirect('login')
    else:
        user_form = UserRegisterForm()
        profile_form = ProfileRegisterForm()

    return render(request, 'ordemServico/registro.html', {'user_form': user_form, 'profile_form': profile_form})
