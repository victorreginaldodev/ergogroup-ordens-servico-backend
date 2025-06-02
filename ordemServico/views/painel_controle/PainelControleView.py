from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
import locale
from django.http import JsonResponse
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from django.utils.timezone import now

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

    # Define o limite de data para o início do mês
    data_limite = now().replace(day=1)

    # Obtém os 10 maiores compradores do mês
    top_compradores = (
        OrdemServico.objects.filter(data_criacao__gte=data_limite)
        .values('cliente__nome')  # Agrupa pelo nome do cliente
        .annotate(total_faturamento=Sum('valor'))  # Soma o faturamento por cliente
        .order_by('-total_faturamento')[:5]  # Ordena pelo maior faturamento e limita a 5
    )

    context = {
        'page_obj': page_obj,
        'top_compradores': top_compradores,
    }

    # Renderiza o template com os dados da primeira página
    return render(request, 'ordemServico/painel_controle/painel_controle.html', context )


@login_required
@user_passes_test(verificar_tipo_usuario)
def servicos_graficos(request):

    data_limite = (datetime.now() - timedelta(days=180)).replace(day=1)

    # 1. Quantidade de serviços criados por mês (sem limite de tempo)
    servicos_por_mes = (
        Servico.objects.filter(ordem_servico__data_criacao__gte=data_limite)
        .annotate(mes=TruncMonth('ordem_servico__data_criacao'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    # 2. Quantidade de serviços por status (sem filtro de data)
    servicos_por_status = (
        Servico.objects.values('status')
        .annotate(total=Count('id'))
        .order_by('status')
    )

    # 3. Valor de vendas por mês (sem limite de tempo)
    vendas_por_mes = (
        OrdemServico.objects.filter(data_criacao__gte=data_limite)
        .annotate(mes=TruncMonth('data_criacao'))
        .values('mes')
        .annotate(total_vendas=Sum('valor'))
        .order_by('mes')
    )

    # Converte os dados para listas para enviar como JSON
    servicos_por_mes = list(servicos_por_mes)
    servicos_por_status = list(servicos_por_status)
    vendas_por_mes = list(vendas_por_mes)

    # Retorna os dados como JSON
    return JsonResponse({
        'servicos_por_mes': servicos_por_mes,
        'servicos_por_status': servicos_por_status,
        'vendas_por_mes': vendas_por_mes,
    })
