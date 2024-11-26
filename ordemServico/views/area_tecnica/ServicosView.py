from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q, F

from ordemServico.models import Servico, Tarefa, Profile
from ordemServico.forms import ServicoUpdateForm, TarefaForm

# Função que verifica se o usuário é 'Diretor', 'Administrativo' ou 'Líder Técnico'
def verificar_tipo_usuario(user):
    try:
        return user.profile.role in [1, 2, 3]
    except Profile.DoesNotExist:
        return False

# Definindo o inlineformset_factory com os campos explicitamente
FormTarefaInlineFormset = inlineformset_factory(
    Servico,
    Tarefa,
    form=TarefaForm,
    fields=['profile', 'descricao'],
    extra=1
)

@user_passes_test(verificar_tipo_usuario)
@login_required
def lider_tecnico(request):
    
    servicos = Servico.objects.all()

    context = {
        'servicos': servicos
    }

    return render(request, 'ordemServico/area_tecnica/servicos.html', context)





# @user_passes_test(verificar_tipo_usuario)
# @login_required
# def tarefas(request, servico_id):
#     servico = get_object_or_404(Servico, id=servico_id)

#     if request.method == 'POST':
#         form = TarefaForm(request.POST)
#         if form.is_valid():
#             tarefa = form.save(commit=False)
#             tarefa.servico = servico  # Aqui associamos o serviço
#             tarefa.save()
#             messages.success(request, 'Tarefa criada com sucesso.')
#             return redirect('tarefas', servico_id=servico.id)
#     else:
#         form = TarefaForm()

#     context = {
#         'servico': servico,
#         'form': form,
#     }

#     return render(request, 'ordemServico/tarefas.html', context)