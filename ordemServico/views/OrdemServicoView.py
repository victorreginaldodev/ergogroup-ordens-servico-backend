from django.shortcuts import render, redirect, get_object_or_404
from django.forms import inlineformset_factory
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator

from ordemServico.forms import OrdemServicoForm, ServicoForm
from ordemServico.models import OrdemServico, Servico, Profile


def verificar_tipo_usuario(user):
    '''
        Função que verifica se o usuário é 'Diretor', 'Administrativo' ou 'Líder Técnico
    '''
    try:
        return user.profile.role in [1, 2, 3, 4]
    except Profile.DoesNotExist:
        return False

@user_passes_test(verificar_tipo_usuario)
@login_required
def listar_ordens_servicos(request):
    # Obtém o parâmetro de busca da URL (se existir)
    busca = request.GET.get('busca', '')

    # Filtra as ordens de serviço pelo nome do cliente (se houver busca)
    if busca:
        ordens_servicos = OrdemServico.objects.filter(
            cliente__nome__icontains=busca
        ).order_by('-data_criacao')
    else:
        ordens_servicos = OrdemServico.objects.all().order_by('-data_criacao')

    # Quantidade de itens por página
    itens_por_pagina = 10
    paginator = Paginator(ordens_servicos, itens_por_pagina)

    # Obtém o número da página da requisição
    pagina = request.GET.get('page')
    ordens_paginadas = paginator.get_page(pagina)

    return render(request, 'ordemServico/ordem_servico/listar_ordens_servicos.html', {
        "ordens_servicos": ordens_paginadas,
        "busca": busca  # Passa o termo de busca para o template
    })

@login_required
@user_passes_test(verificar_tipo_usuario)
def criar_ordem_servico(request):
    ServicoFormSet = inlineformset_factory(
        OrdemServico,
        Servico,
        form=ServicoForm,
        fields='__all__',
        extra=1,
        can_delete=True
    )

    if request.method == 'POST':
        ordem_servico_form = OrdemServicoForm(request.POST)
        servico_formset = ServicoFormSet(request.POST)

        if ordem_servico_form.is_valid() and servico_formset.is_valid():
            # Salva a Ordem de Serviço e associa o usuário criador
            ordem_servico = ordem_servico_form.save(commit=False)
            ordem_servico.usuario_criador = request.user.username
            ordem_servico.save()

            # Associa os serviços à Ordem de Serviço criada
            servico_formset.instance = ordem_servico
            servico_formset.save()

            messages.success(request, "Ordem de Serviço criada com sucesso!")
            return redirect(reverse('criar_ordem_servico'))
        else:
            # Mensagens de erro para formulário inválido
            if not ordem_servico_form.is_valid():
                messages.error(request, "Erro ao salvar a Ordem de Serviço. Verifique os campos.")
            if not servico_formset.is_valid():
                messages.error(request, "Erro ao salvar os serviços. Verifique os campos.")

            context = {
                'ordem_servico_form': ordem_servico_form,
                'servico_formset': servico_formset,
            }
            return render(request, 'ordemServico/ordem_servico/criar_ordem_servico.html', context)

    else:
        ordem_servico_form = OrdemServicoForm()
        servico_formset = ServicoFormSet()

        context = {
            'ordem_servico_form': ordem_servico_form,
            'servico_formset': servico_formset,
        }
        return render(request, 'ordemServico/ordem_servico/criar_ordem_servico.html', context)


@user_passes_test(verificar_tipo_usuario)
@login_required
def editar_ordem_servico(request, pk):
    ordem_servico = get_object_or_404(OrdemServico, pk=pk)

    # Formset para serviços associados à Ordem de Serviço
    ServicoFormSet = inlineformset_factory(
        OrdemServico,
        Servico,
        form=ServicoForm,
        extra=0,  # Nenhum formulário extra
        can_delete=True  # Permitir exclusão de serviços
    )

    if request.method == 'POST':
        # Atualização dos dados
        ordem_servico_form = OrdemServicoForm(request.POST, instance=ordem_servico)
        servico_formset = ServicoFormSet(request.POST, instance=ordem_servico)

        if ordem_servico_form.is_valid() and servico_formset.is_valid():
            # Salvar Ordem de Serviço
            ordem_servico = ordem_servico_form.save()

            # Salvar serviços associados
            servico_formset.save()

            messages.success(request, "Ordem de Serviço atualizada com sucesso!")
            return redirect(reverse('listar_ordens_servicos'))
        else:
            # Log de erros para depuração
            if not ordem_servico_form.is_valid():
                print(ordem_servico_form.errors)
            if not servico_formset.is_valid():
                print(servico_formset.errors)
            messages.error(request, "Erro ao salvar a Ordem de Serviço. Verifique os campos.")

    else:
        # Pré-carregar dados existentes
        ordem_servico_form = OrdemServicoForm(instance=ordem_servico)
        servico_formset = ServicoFormSet(instance=ordem_servico)

    context = {
        'ordem_servico_form': ordem_servico_form,
        'servico_formset': servico_formset,
        'ordem_servico': ordem_servico,
    }
    return render(request, 'ordemServico/ordem_servico/editar_ordem_servico.html', context)