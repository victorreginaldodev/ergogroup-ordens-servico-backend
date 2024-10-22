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
    # Filtra serviços com status 'em_espera'
    novos_servicos = Servico.objects.filter(status='em_espera')
    qtd_novos_servicos = novos_servicos.count()

    servicos_em_andamento = Servico.objects.annotate(
        total_tarefas=Count('tarefas'),
        tarefas_concluidas=Count('tarefas', filter=Q(tarefas__status='concluida'))
    ).filter(
        total_tarefas__gt=0,  # Certifica-se de que o serviço tenha tarefas
        tarefas_concluidas__lt=F('total_tarefas'),  # Verifica se nem todas as tarefas estão concluídas
        status='em_andamento'  # O status do serviço é 'em andamento'
    )
    qtd_servicos_em_andamento = servicos_em_andamento.count()

    # Filtra serviços concluídos
    servicos_finalizados = Servico.objects.filter(status='concluida')
    qtd_servicos_finalizados = servicos_finalizados.count()

    servicos_para_finalizar = Servico.objects.annotate(
        total_tarefas=Count('tarefas'),
        tarefas_concluidas=Count('tarefas', filter=Q(tarefas__status='concluida'))
    ).filter(
        total_tarefas__gt=0,
        total_tarefas=F('tarefas_concluidas'),
        status='em_andamento'
    )
    qtd_servicos_para_finalizar = servicos_para_finalizar.count()

    # Lógica para formulário de atualização de serviço
    if request.method == 'POST' and 'formUpdate' in request.POST:
        servico_id = request.POST.get('servico_id')
        servico = get_object_or_404(Servico, id=servico_id)
        formUpdate = ServicoUpdateForm(request.POST, instance=servico)

        if formUpdate.is_valid():
            formUpdate.save()
            messages.success(request, 'Serviço atualizado com sucesso.')
            return redirect('lider_tecnico')
        else:
            messages.error(request, 'Erro ao tentar atualizar o serviço.')
    else:
        formUpdate = ServicoUpdateForm()

    # Lógica para formulário de criação de tarefas
    if request.method == 'POST' and 'formTarefa' in request.POST:
        servico_id = request.POST.get('servico_id')
        servico = get_object_or_404(Servico, id=servico_id)
        form_tarefa = FormTarefaInlineFormset(request.POST, instance=servico)

        if form_tarefa.is_valid():
            form_tarefa.save()
            messages.success(request, 'Tarefas adicionadas com sucesso.')
            return redirect('lider_tecnico')
        else:
            messages.error(request, 'Erro ao tentar adicionar tarefas ao serviço.')
    else:
        servico_id = request.GET.get('servico_id')
        servico = get_object_or_404(Servico, id=servico_id) if servico_id else None
        form_tarefa = FormTarefaInlineFormset(instance=servico)

    context = {
        'novos_servicos': novos_servicos,
        'qtd_novos_servicos': qtd_novos_servicos,

        'servicos_em_andamento': servicos_em_andamento,
        'qtd_servicos_em_andamento': qtd_servicos_em_andamento,

        'servicos_finalizados': servicos_finalizados,
        'qtd_servicos_finalizados': qtd_servicos_finalizados,

        'servicos_para_finalizar': servicos_para_finalizar,
        'qtd_servicos_para_finalizar': qtd_servicos_para_finalizar,

        'formUpdate': formUpdate,
        'form_tarefa': form_tarefa,
    }

    return render(request, 'ordemServico/lider_tecnico.html', context)

@user_passes_test(verificar_tipo_usuario)
@login_required
def tarefas(request, servico_id):
    servico = get_object_or_404(Servico, id=servico_id)

    if request.method == 'POST':
        form = TarefaForm(request.POST)
        if form.is_valid():
            tarefa = form.save(commit=False)
            tarefa.servico = servico  # Aqui associamos o serviço
            tarefa.save()
            messages.success(request, 'Tarefa criada com sucesso.')
            return redirect('tarefas', servico_id=servico.id)
    else:
        form = TarefaForm()

    context = {
        'servico': servico,
        'form': form,
    }

    return render(request, 'ordemServico/tarefas.html', context)

