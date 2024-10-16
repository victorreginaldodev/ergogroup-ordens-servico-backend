from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ordemServico.forms import OsRapidaForm, OsRapidaUpdateForm, OsRapidaFullUpdateForm
from ordemServico.models import MiniOS

@login_required
def criar_os_rapida(request):
    if request.method == 'GET':
        form = OsRapidaForm()
        context = {'form': form}
        return render(request, 'ordemServico/criar_os_rapida.html', context)

    elif request.method == 'POST':
        form = OsRapidaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('criar_os_rapida'))
        else:
            context = {'form': form}
            return render(request, 'ordemServico/criar_os_rapida.html', context)


@login_required
def editar_os_rapida(request, os_rapida_id):
    os_rapida = get_object_or_404(MiniOS, id=os_rapida_id)

    if request.method == 'POST':
        form = OsRapidaFullUpdateForm(request.POST, instance=os_rapida)

        if form.is_valid():
            form.save()
            return redirect('os_rapida')
    else:
        form = OsRapidaFullUpdateForm(instance=os_rapida)

    context = {
        'form': form,
        'os_rapida_id': os_rapida_id 
    }
    return render(request, 'ordemServico/editar_os_rapida.html', context)


@login_required
def os_rapida(request):
    profile = request.user.profile

    os_rapidas_nao_iniciadas = MiniOS.objects.filter(status='nao_iniciado', profile=profile)
    qtd_os_rapidas_nao_iniciadas = os_rapidas_nao_iniciadas.count()

    os_rapidas_em_andamento = MiniOS.objects.filter(status='em_andamento', profile=profile)
    qtd_os_rapidas_em_andamento = os_rapidas_em_andamento.count()

    os_rapidas_finalizadas = MiniOS.objects.filter(status='finalizada', profile=profile)
    qtd_os_rapidas_finalizadas = os_rapidas_finalizadas.count()

    # Inicializa o formulário de atualização como None
    formUpdate = None

    # Processa o formulário de atualização, se enviado
    if request.method == 'POST':
        os_rapida_id = request.POST.get('os_rapida_id')
        os_rapida = get_object_or_404(MiniOS, id=os_rapida_id)
        
        formUpdate = OsRapidaUpdateForm(request.POST, instance=os_rapida)

        if formUpdate.is_valid():
            os_rapida = formUpdate.save(commit=False)

            # Preserva a data de início se não for enviada no formulário
            if not formUpdate.cleaned_data.get('data_inicio'):
                os_rapida.data_inicio = MiniOS.objects.get(id=os_rapida_id).data_inicio

            os_rapida.save()
            messages.success(request, 'OS rápida atualizada com sucesso.')
            return redirect('os_rapida')
        else:
            messages.error(request, 'Erro ao tentar atualizar a OS rápida.')
    
    # Caso não tenha sido enviado, cria um novo formulário de atualização vazio para o template
    if formUpdate is None:
        formUpdate = OsRapidaUpdateForm()

    context = {
        'os_rapidas_nao_iniciadas': os_rapidas_nao_iniciadas,
        'qtd_os_rapidas_nao_iniciadas': qtd_os_rapidas_nao_iniciadas,
        'os_rapidas_em_andamento': os_rapidas_em_andamento,
        'qtd_os_rapidas_em_andamento': qtd_os_rapidas_em_andamento,
        'os_rapidas_finalizadas': os_rapidas_finalizadas,
        'qtd_os_rapidas_finalizadas': qtd_os_rapidas_finalizadas,
        'formUpdate': formUpdate, 
    }

    return render(request, 'ordemServico/os_rapida.html', context)
