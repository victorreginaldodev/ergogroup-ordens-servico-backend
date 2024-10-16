from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ordemServico.models import Tarefa
from ordemServico.forms import TarefaUpdateForm

@login_required
def tecnico(request):
    profile = request.user.profile

    # Filtra as tarefas conforme o status e o perfil do usuário
    tarefas_nao_iniciadas = Tarefa.objects.filter(status='nao_iniciada', profile=profile)
    qtd_tarefas_nao_iniciadas = tarefas_nao_iniciadas.count()

    tarefas_em_andamento = Tarefa.objects.filter(status='em_andamento', profile=profile)
    qtd_tarefas_em_andamento = tarefas_em_andamento.count()

    tarefas_finalizadas = Tarefa.objects.filter(status='concluida', profile=profile)
    qtd_tarefas_finalizadas = tarefas_finalizadas.count()

    # Verifica se o método é POST, ou seja, se o formulário foi submetido
    if request.method == 'POST':
        tarefa_id = request.POST.get('tarefa_id')

        if tarefa_id:  # Verifica se o ID da tarefa foi enviado
            tarefa = get_object_or_404(Tarefa, id=tarefa_id, profile=profile)  # Confirma que a tarefa pertence ao usuário logado

            formUpdate = TarefaUpdateForm(request.POST, instance=tarefa)

            if formUpdate.is_valid():
                formUpdate.save()  # Salva a tarefa com os dados do formulário
                messages.success(request, 'Tarefa atualizada com sucesso.')
                return redirect('tecnico')  # Redireciona para evitar reenvio de dados
            else:
                messages.error(request, 'Erro ao tentar atualizar tarefa.')
        else:
            messages.error(request, 'Nenhuma tarefa foi selecionada para atualização.')

    else:
        formUpdate = TarefaUpdateForm()  # Inicializa um formulário vazio caso seja um GET

    context = {
        'tarefas_nao_iniciadas': tarefas_nao_iniciadas,
        'qtd_tarefas_nao_iniciadas': qtd_tarefas_nao_iniciadas,
        'tarefas_em_andamento': tarefas_em_andamento,
        'qtd_tarefas_em_andamento': qtd_tarefas_em_andamento,
        'tarefas_finalizadas': tarefas_finalizadas,
        'qtd_tarefas_finalizadas': qtd_tarefas_finalizadas,
        'formUpdate': formUpdate,  # O formulário atualizado para a tarefa em questão
    }

    return render(request, 'ordemServico/tecnico.html', context)
