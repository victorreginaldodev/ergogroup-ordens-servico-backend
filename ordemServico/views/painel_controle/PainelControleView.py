from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
import locale
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth

from ordemServico.models import Profile, OrdemServico, Servico

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def verificar_tipo_usuario(user):
    try:
        return user.profile.role in [1, 2, 3]
    except Profile.DoesNotExist:
        return False


@login_required
@user_passes_test(verificar_tipo_usuario)
def painel_controle_template(request):
    # Carrega os serviços e aplica paginação para a primeira página
    servicos = Servico.objects.select_related('ordem_servico__cliente', 'repositorio').order_by('-ordem_servico__data_criacao')
    paginator = Paginator(servicos, 10)  # 10 serviços por página
    page_number = 1
    page_obj = paginator.get_page(page_number)

    # Renderiza o template com os dados da primeira página
    return render(request, 'ordemServico/painel_controle/painel_controle.html', {'page_obj': page_obj})

@login_required
@user_passes_test(verificar_tipo_usuario)
def painel_controle_dados(request):
    # Obtem os filtros enviados via GET
    search_query = request.GET.get('search', '').strip().lower()
    status_filter = request.GET.get('status', '')

    # Filtra os serviços
    servicos = Servico.objects.select_related('ordem_servico__cliente', 'repositorio').order_by('-ordem_servico__data_criacao')

    if search_query:
        servicos = servicos.filter(ordem_servico__cliente__nome__icontains=search_query)
    if status_filter:
        servicos = servicos.filter(status=status_filter)

    # Verifica se os filtros estão ativos para retornar todos os resultados
    filtro_aplicado = search_query or status_filter
    if filtro_aplicado:
        servicos = list(servicos.values(
            'id',
            'ordem_servico__cliente__nome',
            'repositorio__nome',
            'ordem_servico__data_criacao',
            'data_conclusao',
            'status',
        ))
        return JsonResponse({'servicos': servicos, 'filtro_aplicado': True})

    # Caso contrário, mantém a paginação
    paginator = Paginator(servicos, 10)  # 10 serviços por página
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Retorna os dados paginados
    servicos = list(page_obj.object_list.values(
        'id',
        'ordem_servico__cliente__nome',
        'repositorio__nome',
        'ordem_servico__data_criacao',
        'data_conclusao',
        'status',
    ))
    return JsonResponse({
        'servicos': servicos,
        'filtro_aplicado': False,
        'has_previous': page_obj.has_previous(),
        'has_next': page_obj.has_next(),
        'previous_page': page_obj.previous_page_number() if page_obj.has_previous() else None,
        'next_page': page_obj.next_page_number() if page_obj.has_next() else None,
        'total_pages': paginator.num_pages,
        'current_page': page_obj.number,
    })


@login_required
@user_passes_test(verificar_tipo_usuario)
def detalhe_servico_modal(request, servico_id):
    servico = get_object_or_404(Servico, id=servico_id)
    data = {
        'cliente': servico.ordem_servico.cliente.nome,
        'servico': servico.repositorio.nome,
        'data_recebimento': servico.ordem_servico.data_criacao.strftime('%d/%m/%Y'),
        'data_conclusao': servico.data_conclusao.strftime('%d/%m/%Y') if servico.data_conclusao else None,
        'status': servico.get_status_display(),
        'descricao': servico.descricao,
    }
    return JsonResponse(data)



@login_required
@user_passes_test(verificar_tipo_usuario)
def servicos_graficos(request):
    # 1. Quantidade de serviços criados por mês
    servicos_por_mes = (
        Servico.objects.filter(ordem_servico__data_criacao__isnull=False)
        .annotate(mes=TruncMonth('ordem_servico__data_criacao'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    # 2. Quantidade de serviços por status
    servicos_por_status = (
        Servico.objects.values('status')
        .annotate(total=Count('id'))
        .order_by('status')
    )

    # 3. Valor de vendas por mês
    vendas_por_mes = (
        OrdemServico.objects.filter(data_criacao__isnull=False)
        .annotate(mes=TruncMonth('data_criacao'))
        .values('mes')
        .annotate(total_vendas=Sum('valor'))
        .order_by('mes')
    )

    # Converte os dados para listas para serem enviados como JSON
    servicos_por_mes = list(servicos_por_mes)
    servicos_por_status = list(servicos_por_status)
    vendas_por_mes = list(vendas_por_mes)

    # Retorna os dados como JSON
    return JsonResponse({
        'servicos_por_mes': servicos_por_mes,
        'servicos_por_status': servicos_por_status,
        'vendas_por_mes': vendas_por_mes,
    })
