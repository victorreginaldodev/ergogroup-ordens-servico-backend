from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Case, When, Value, IntegerField, Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

from ordemServico.forms import OsRapidaForm, OsRapidaUpdateForm, OsRapidaFullUpdateForm
from ordemServico.models import MiniOS, Profile


@login_required
def listar_os_rapidas(request):
    # Captura os filtros enviados pelo front-end
    pesquisa = request.GET.get('pesquisa', '').strip().lower()
    status = request.GET.get('status', '').strip()
    colaborador_id = request.GET.get('colaborador', '').strip()

    # Obtém o usuário autenticado e o perfil associado
    user = request.user
    profile = user.profile

    # Regra de negócio para exibição das MiniOS
    if profile.role in [1, 2, 3]:  # Exibe todas as MiniOS
        mini_os_list = MiniOS.objects.all()
    elif profile.role in [4, 5]:  # Exibe MiniOS relacionadas ao colaborador
        mini_os_list = MiniOS.objects.filter(profile=profile)
    else:  # Papel inválido, retorna queryset vazio
        mini_os_list = MiniOS.objects.none()

    # Otimização de consultas
    mini_os_list = mini_os_list.select_related('cliente', 'servico', 'profile')

    # Aplicar filtros
    if pesquisa:
        mini_os_list = mini_os_list.filter(
            Q(cliente__nome__icontains=pesquisa) |
            Q(servico__nome__icontains=pesquisa)
        )
    
    if status and status != 'todos':  # Filtrar por status
        mini_os_list = mini_os_list.filter(status=status)
    
    if colaborador_id:  # Filtrar por colaborador
        mini_os_list = mini_os_list.filter(profile_id=colaborador_id)

    # Ordenação por prioridade de status e data de recebimento
    mini_os_list = mini_os_list.annotate(
        status_priority=Case(
            When(status='nao_iniciado', then=Value(1)),
            When(status='em_andamento', then=Value(2)),
            When(status='finalizada', then=Value(3)),
            default=Value(4),
            output_field=IntegerField()
        )
    ).order_by('status_priority', 'data_recebimento')

    # Paginação
    paginator = Paginator(mini_os_list, 20)
    page_number = int(request.GET.get('page', 1))
    page_obj = paginator.get_page(page_number)

    # Perfis para o filtro de colaboradores
    profiles = Profile.objects.filter(role__in=[3, 4, 5]).select_related('user').order_by('user__username')

    # Resposta AJAX
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [
            {
                "id": mini_os.id,
                "cliente_nome": mini_os.cliente.nome.upper() if mini_os.cliente else "Não informado",
                "tipo_inscricao_display": mini_os.cliente.get_tipo_inscricao_display() if mini_os.cliente else "Não informado",
                "numero_inscricao": mini_os.cliente.numero_inscricao if mini_os.cliente else "Não informado",
                "tipo_cliente_display": mini_os.cliente.get_tipo_cliente_display() if mini_os.cliente else "Não informado",
                "nome_representante": mini_os.cliente.nome_representante if mini_os.cliente else "Não cadastrado",
                "setor_representante": mini_os.cliente.setor_representante if mini_os.cliente else "Não cadastrado",
                "email_representante": mini_os.cliente.email_representante if mini_os.cliente else "Não cadastrado",
                "telefone_representante": mini_os.cliente.contato_representante if mini_os.cliente else "Não cadastrado",
                "servico_nome": mini_os.servico.nome if mini_os.servico else "Não informado",
                "quantidade": mini_os.quantidade,
                "descricao": mini_os.descricao,
                "data_recebimento": mini_os.data_recebimento if mini_os.data_recebimento else "Não recebido",
                "data_inicio": mini_os.data_inicio if mini_os.data_inicio else "NÃO INICIADO",
                "data_termino": mini_os.data_termino if mini_os.data_termino else "NÃO CONCLUÍDO",
                "status": mini_os.get_status_display(),
                "form_update": {
                    "id": mini_os.id,
                    "status": OsRapidaUpdateForm(instance=mini_os)['status'].as_widget(),
                    "data_termino": OsRapidaUpdateForm(instance=mini_os)['data_termino'].as_widget(),
                },
                "profile": str(mini_os.profile),
            }
            for mini_os in page_obj
        ]
        return JsonResponse({
            "mini_os": data,
            "has_previous": page_obj.has_previous(),
            "has_next": page_obj.has_next(),
            "previous_page_number": page_obj.previous_page_number() if page_obj.has_previous() else None,
            "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
        })

    # Renderização padrão
    return render(
        request,
        "ordemServico/area_tecnica/os_rapida.html",
        {
            "mini_os_list": page_obj,
            "full_update_form": OsRapidaFullUpdateForm(),
            "profiles": profiles,
        }
    )


@csrf_exempt
def atualizar_mini_os(request, mini_os_id):
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        mini_os = get_object_or_404(MiniOS, id=mini_os_id)
        form = OsRapidaUpdateForm(request.POST, instance=mini_os)

        if form.is_valid():
            form.save()
            return JsonResponse({
                'success': True,
                'status': mini_os.get_status_display(),
                'data_inicio': mini_os.data_inicio.strftime('%Y-%m-%d') if mini_os.data_inicio else None,
                'data_termino': mini_os.data_termino.strftime('%Y-%m-%d') if mini_os.data_termino else None,
            })
        else:
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

    return JsonResponse({'success': False, 'error': 'Método inválido'}, status=405)


@login_required
def criar_os_rapida(request):
    if request.method == 'GET':
        form = OsRapidaForm()
        context = {'form': form}
        return render(request, 'ordemServico/area_tecnica/criar_os_rapida.html', context)

    elif request.method == 'POST':
        form = OsRapidaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse('criar_os_rapida'))
        else:
            context = {'form': form}
            return render(request, 'ordemServico/area_tecnica/criar_os_rapida.html', context)


@login_required
def editar_os_rapida(request, os_rapida_id):
    os_rapida = get_object_or_404(MiniOS, id=os_rapida_id)

    if request.method == 'POST':
        form = OsRapidaFullUpdateForm(request.POST, instance=os_rapida)

        if form.is_valid():
            form.save()
            messages.success(request, "Ordem de Serviço atualizada com sucesso.")
            return redirect('os_rapida')
        else:
            messages.error(request, "Erro ao atualizar a Ordem de Serviço. Verifique os campos.")
    else:
        form = OsRapidaFullUpdateForm(instance=os_rapida)

    context = {
        'form': form,
        'os_rapida_id': os_rapida_id
    }
    return render(request, 'ordemServico/area_tecnica/editar_os_rapida.html', context)
