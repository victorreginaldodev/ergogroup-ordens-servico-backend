from django.shortcuts import render

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count

from django.http import JsonResponse
from django.db.models.functions import TruncMonth
from django.utils import timezone
from datetime import timedelta

from ordemServico.models import Servico, Tarefa, Profile


def verificar_tipo_usuario(user):
    try:
        return user.profile.role in [1, 2, 3]
    except Profile.DoesNotExist:
        return False


@user_passes_test(verificar_tipo_usuario)
@login_required
def dashborad_lider(request):
    return render(request, 'ordemServico/area_tecnica/dashboard_servicos.html')


STATUS_DISPLAY = {
    'em_espera': 'EM ESPERA',
    'em_andamento': 'EM ANDAMENTO',
    'concluida': 'CONCLUÍDA',
}

@user_passes_test(verificar_tipo_usuario)
@login_required
def servicos_por_status(request):
    contagem = Servico.objects.values('status').order_by('status').annotate(total=Count('id'))
    dados = {STATUS_DISPLAY[item['status']]: item['total'] for item in contagem}
    return JsonResponse(dados)


@user_passes_test(verificar_tipo_usuario)
@login_required
def conclusao_servicos_por_mes(request):
    # Define o intervalo de 6 meses a partir da data atual
    data_limite = timezone.now().date().replace(day=1) - timedelta(days=360) 

    # Filtra os serviços concluídos nos últimos 6 meses e agrupa por mês
    dados_conclusao = (
        Servico.objects
        .filter(status='concluida', data_conclusao__gte=data_limite)
        .annotate(mes_conclusao=TruncMonth('data_conclusao'))
        .values('mes_conclusao')
        .annotate(total=Count('id'))
        .order_by('mes_conclusao')
    )

    # Formata a data para "mês/ano" ao invés de "ano/mês"
    dados = {
        item['mes_conclusao'].strftime('%m/%Y'): item['total']
        for item in dados_conclusao
        if item['mes_conclusao']
    }
    return JsonResponse(dados)


@user_passes_test(verificar_tipo_usuario)
@login_required
def lista_profiles(request):
    profiles = Profile.objects.values('id', 'nome')
    return JsonResponse(list(profiles), safe=False)

@user_passes_test(verificar_tipo_usuario)
@login_required
def tarefas_por_status(request, profile_id=None):
    if profile_id:
        data = (
            Tarefa.objects.filter(profile_id=profile_id)
            .values('status')
            .annotate(total=Count('status'))
        )
    else:
        data = (
            Tarefa.objects
            .values('status')
            .annotate(total=Count('status'))
        )
    status_data = {item['status']: item['total'] for item in data}
    return JsonResponse(status_data)