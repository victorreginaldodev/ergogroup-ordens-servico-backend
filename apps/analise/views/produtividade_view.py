from datetime import date, datetime, time

from django.db.models import Count, Max, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.analise.serializers import ProdutividadeResponseSerializer
from apps.analise.utils import gerar_intervalo_meses, preencher_meses
from apps.contas.models.choices import TipoUsuario
from apps.ordens_servico.models import OrdemServico, Prioridade
from apps.ordens_servico.models.ordem_servico import Status as StatusOS
from apps.ordens_servico.models import Servico
from apps.ordens_servico.models.servico import StatusServico
from apps.ordens_servico.models import Tarefa, OrdemServicoOperacional
from apps.ordens_servico.models.tarefa import StatusTarefa
from apps.ordens_servico.models.ordem_servico_operacional import StatusOrdemServicoOperacional


class ProdutividadeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Indicadores de execução técnica',
        description=(
            'Indicadores operacionais dos últimos 12 meses: tempos médios de '
            'execução, taxa de cancelamento e análise individual por técnico '
            '(concluídos, carga de trabalho atual e tempo médio). Não contém '
            'valores monetários nem dados de clientes — disponível para '
            'qualquer perfil autenticado. Técnicos veem apenas a própria '
            'linha em `por_tecnico`.'
        ),
        responses={200: ProdutividadeResponseSerializer},
    )
    def get(self, request):
        hoje = timezone.now().date()
        meses = gerar_intervalo_meses(hoje, 12)
        data_inicio = date(meses[0]['ano'], meses[0]['mes'], 1)

        return Response({
            'tempos_medios': self._tempos_medios(data_inicio),
            'taxa_cancelamento': self._taxa_cancelamento(data_inicio),
            'por_tecnico': self._por_tecnico(data_inicio, meses, request.user),
        })

    # ------------------------------------------------------------------ #

    def _tempos_medios(self, data_inicio):
        # Todos os pares (venda, fim_real) de OS concluídas — sem filtro de data.
        # A distribuição e a média global precisam refletir o histórico completo do banco.
        todos_pares = list(
            OrdemServico.objects
            .filter(concluida=True)
            .annotate(
                data_fim_real=Max(
                    'servicos__data_termino',
                    filter=Q(servicos__status='concluida'),
                )
            )
            .filter(data_fim_real__isnull=False)
            .values_list('data_venda', 'data_fim_real')
        )

        servicos_concluidos = Servico.objects.filter(
            status=StatusServico.CONCLUIDA,
            data_inicio__isnull=False,
            data_termino__isnull=False,
        )
        servico_media = _media_dias(servicos_concluidos.values_list('data_inicio', 'data_termino'))

        tarefas_com_inicio = Tarefa.objects.filter(
            data_inicio__isnull=False,
        )
        lead_time_media = _media_dias(
            (timezone.localtime(criada_em).date(), inicio)
            for inicio, criada_em in tarefas_com_inicio.values_list('data_inicio', 'criada_em')
        )

        return {
            'os_criacao_para_encerramento_dias': _media_dias(todos_pares),
            'os_criacao_para_conclusao_dias': _media_dias_criacao_para_conclusao_os(),
            'os_total_com_data': len(todos_pares),
            'os_distribuicao_tempo': _distribuicao_tempo_os(todos_pares),
            'servicos_inicio_para_fim_dias': servico_media,
            'tarefa_criacao_para_inicio_dias': lead_time_media,
            'tempo_por_catalogo': _tempo_por_catalogo(),
        }

    def _taxa_cancelamento(self, data_inicio):
        # Comparação direta com datetime timezone-aware (em vez de `__date`),
        # pois `__date` em DateTimeField exige CONVERT_TZ do MySQL, que falha
        # silenciosamente (retorna NULL) quando as tabelas de timezone do
        # servidor não estão carregadas.
        limite = timezone.make_aware(datetime.combine(data_inicio, time.min))
        tarefas_periodo = Tarefa.objects.filter(criada_em__gte=limite)
        servicos_periodo = Servico.objects.filter(criado_em__gte=limite)
        return {
            'tarefas': _bloco_cancelamento(tarefas_periodo, StatusTarefa.CANCELADA),
            'servicos': _bloco_cancelamento(servicos_periodo, StatusServico.CANCELADO),
        }

    def _por_tecnico(self, data_inicio, meses, usuario):
        hoje = timezone.localdate()

        # Histórico completo — para KPIs absolutos e tempo médio
        tarefas_hist_qs = Tarefa.objects.filter(
            status=StatusTarefa.CONCLUIDA,
            data_termino__isnull=False,
        )
        minios_hist_qs = OrdemServicoOperacional.objects.filter(
            status=StatusOrdemServicoOperacional.FINALIZADA,
            data_termino__isnull=False,
        )
        # Últimos 12 meses — apenas para o gráfico mensal
        tarefas_concluidas_qs = tarefas_hist_qs.filter(data_termino__gte=data_inicio)
        minios_concluidas_qs  = minios_hist_qs.filter(data_termino__gte=data_inicio)

        tarefas_abertas_qs = Tarefa.objects.filter(
            status__in=[StatusTarefa.ABERTA, StatusTarefa.EM_ANDAMENTO],
        )
        minios_abertas_qs = OrdemServicoOperacional.objects.filter(
            status__in=[StatusOrdemServicoOperacional.NAO_INICIADO, StatusOrdemServicoOperacional.EM_ANDAMENTO],
        )
        tarefas_atrasadas_qs = tarefas_abertas_qs.filter(prazo__isnull=False, prazo__lt=hoje)
        minios_atrasadas_qs = minios_abertas_qs.filter(prazo__isnull=False, prazo__lt=hoje)
        tarefas_alta_prioridade_qs = tarefas_abertas_qs.filter(prioridade=Prioridade.ALTA)
        minios_alta_prioridade_qs = minios_abertas_qs.filter(prioridade=Prioridade.ALTA)

        if usuario.tipo_usuario == TipoUsuario.TECNICO:
            tarefas_hist_qs        = tarefas_hist_qs.filter(responsavel=usuario)
            minios_hist_qs         = minios_hist_qs.filter(responsavel=usuario)
            tarefas_concluidas_qs  = tarefas_concluidas_qs.filter(responsavel=usuario)
            minios_concluidas_qs   = minios_concluidas_qs.filter(responsavel=usuario)
            tarefas_abertas_qs     = tarefas_abertas_qs.filter(responsavel=usuario)
            minios_abertas_qs      = minios_abertas_qs.filter(responsavel=usuario)
            tarefas_atrasadas_qs   = tarefas_atrasadas_qs.filter(responsavel=usuario)
            minios_atrasadas_qs    = minios_atrasadas_qs.filter(responsavel=usuario)
            tarefas_alta_prioridade_qs = tarefas_alta_prioridade_qs.filter(responsavel=usuario)
            minios_alta_prioridade_qs  = minios_alta_prioridade_qs.filter(responsavel=usuario)

        dados = {}
        duracoes_por_tecnico = {}
        complexidades_por_tecnico = {}
        horas_entregues_por_tecnico = {}
        tarefas_concluidas_por_mes = _mapa_por_responsavel_e_mes(tarefas_concluidas_qs, 'data_termino')
        minios_concluidas_por_mes  = _mapa_por_responsavel_e_mes(minios_concluidas_qs, 'data_termino')

        # KPIs e tempo médio usam o histórico completo
        for (
            responsavel_id, nome, inicio, termino, complexidade_servico, complexidade_catalogo,
            horas_tarefa, horas_servico, horas_catalogo,
        ) in tarefas_hist_qs.values_list(
            'responsavel_id', 'responsavel__nome_completo', 'data_inicio', 'data_termino',
            'servico__complexidade', 'servico__catalogo__complexidade',
            'horas_estimadas', 'servico__horas_estimadas', 'servico__catalogo__horas_estimadas',
        ):
            entry = dados.setdefault(responsavel_id, _linha_tecnico(responsavel_id, nome))
            entry['tarefas_concluidas'] += 1
            if inicio and termino:
                duracoes_por_tecnico.setdefault(responsavel_id, []).append((termino - inicio).days)
            complexidade_efetiva = complexidade_servico if complexidade_servico is not None else complexidade_catalogo
            if complexidade_efetiva is not None:
                complexidades_por_tecnico.setdefault(responsavel_id, []).append(complexidade_efetiva)
            horas_efetivas = horas_tarefa if horas_tarefa is not None else (
                horas_servico if horas_servico is not None else horas_catalogo
            )
            if horas_efetivas is not None:
                horas_entregues_por_tecnico[responsavel_id] = (
                    horas_entregues_por_tecnico.get(responsavel_id, 0) + horas_efetivas
                )

        for responsavel_id, nome in minios_hist_qs.values_list('responsavel_id', 'responsavel__nome_completo'):
            entry = dados.setdefault(responsavel_id, _linha_tecnico(responsavel_id, nome))
            entry['mini_os_concluidas'] += 1

        for item in tarefas_abertas_qs.values('responsavel_id', 'responsavel__nome_completo').annotate(total=Count('id')):
            entry = dados.setdefault(
                item['responsavel_id'], _linha_tecnico(item['responsavel_id'], item['responsavel__nome_completo'])
            )
            entry['tarefas_em_aberto'] = item['total']

        for item in minios_abertas_qs.values('responsavel_id', 'responsavel__nome_completo').annotate(total=Count('id')):
            entry = dados.setdefault(
                item['responsavel_id'], _linha_tecnico(item['responsavel_id'], item['responsavel__nome_completo'])
            )
            entry['mini_os_em_aberto'] = item['total']

        for item in tarefas_atrasadas_qs.values('responsavel_id', 'responsavel__nome_completo').annotate(total=Count('id')):
            entry = dados.setdefault(
                item['responsavel_id'], _linha_tecnico(item['responsavel_id'], item['responsavel__nome_completo'])
            )
            entry['tarefas_atrasadas'] = item['total']

        for item in minios_atrasadas_qs.values('responsavel_id', 'responsavel__nome_completo').annotate(total=Count('id')):
            entry = dados.setdefault(
                item['responsavel_id'], _linha_tecnico(item['responsavel_id'], item['responsavel__nome_completo'])
            )
            entry['mini_os_atrasadas'] = item['total']

        for item in tarefas_alta_prioridade_qs.values('responsavel_id', 'responsavel__nome_completo').annotate(total=Count('id')):
            entry = dados.setdefault(
                item['responsavel_id'], _linha_tecnico(item['responsavel_id'], item['responsavel__nome_completo'])
            )
            entry['tarefas_alta_prioridade_abertas'] = item['total']

        for item in minios_alta_prioridade_qs.values('responsavel_id', 'responsavel__nome_completo').annotate(total=Count('id')):
            entry = dados.setdefault(
                item['responsavel_id'], _linha_tecnico(item['responsavel_id'], item['responsavel__nome_completo'])
            )
            entry['mini_os_alta_prioridade_abertas'] = item['total']

        for responsavel_id, entry in dados.items():
            duracoes = duracoes_por_tecnico.get(responsavel_id) or []
            entry['tempo_medio_tarefa_dias'] = (
                round(sum(duracoes) / len(duracoes), 1) if duracoes else None
            )
            complexidades = complexidades_por_tecnico.get(responsavel_id) or []
            entry['complexidade_media_concluidas'] = (
                round(sum(complexidades) / len(complexidades), 1) if complexidades else None
            )
            entry['horas_estimadas_entregues'] = horas_entregues_por_tecnico.get(responsavel_id, 0)
            entry['tarefas_concluidas_por_mes'] = preencher_meses(
                meses, tarefas_concluidas_por_mes.get(responsavel_id, {})
            )
            entry['mini_os_concluidas_por_mes'] = preencher_meses(
                meses, minios_concluidas_por_mes.get(responsavel_id, {})
            )

        return sorted(dados.values(), key=lambda d: d['tecnico_nome'] or '')


def _mapa_por_responsavel_e_mes(queryset, campo_data: str) -> dict:
    mapa = {}
    for item in (
        queryset
        .annotate(mes=TruncMonth(campo_data))
        .values('responsavel_id', 'mes')
        .annotate(total=Count('id'))
    ):
        mapa.setdefault(item['responsavel_id'], {})[item['mes']] = item['total']
    return mapa


def _linha_tecnico(responsavel_id, nome):
    return {
        'tecnico_id': responsavel_id,
        'tecnico_nome': nome,
        'tarefas_concluidas': 0,
        'tempo_medio_tarefa_dias': None,
        'complexidade_media_concluidas': None,
        'horas_estimadas_entregues': 0,
        'mini_os_concluidas': 0,
        'tarefas_em_aberto': 0,
        'mini_os_em_aberto': 0,
        'tarefas_atrasadas': 0,
        'mini_os_atrasadas': 0,
        'tarefas_alta_prioridade_abertas': 0,
        'mini_os_alta_prioridade_abertas': 0,
        'tarefas_concluidas_por_mes': [],
        'mini_os_concluidas_por_mes': [],
    }


def _bloco_cancelamento(queryset, status_cancelado) -> dict:
    total = queryset.count()
    canceladas = queryset.filter(status=status_cancelado).count()
    return {
        'total': total,
        'canceladas': canceladas,
        'percentual': round(canceladas / total * 100, 1) if total else None,
    }


def _media_dias(pares_datas, inclusivo=False) -> float | None:
    diffs = [
        (fim - inicio).days + (1 if inclusivo else 0)
        for inicio, fim in pares_datas
        if inicio and fim
    ]
    if not diffs:
        return None
    return round(sum(diffs) / len(diffs), 1)


def _media_dias_criacao_para_conclusao_os() -> float | None:
    pares = (
        (
            timezone.localtime(criada_em).date(),
            timezone.localtime(conclusao_em).date(),
        )
        for criada_em, conclusao_em in OrdemServico.objects
        .filter(liberada_para_cobranca_em__isnull=False)
        .values_list('criada_em', 'liberada_para_cobranca_em')
    )
    return _media_dias(pares, inclusivo=True)


def _tempo_por_catalogo() -> list[dict]:
    rows = (
        Servico.objects
        .filter(
            status=StatusServico.CONCLUIDA,
            catalogo__isnull=False,
            data_inicio__isnull=False,
            data_termino__isnull=False,
        )
        .values_list(
            'catalogo_id', 'catalogo__nome', 'catalogo__horas_estimadas', 'catalogo__complexidade',
            'data_inicio', 'data_termino',
        )
    )
    mapa: dict[int, dict] = {}
    for cat_id, cat_nome, horas_estimadas, complexidade, inicio, termino in rows:
        dias = (termino - inicio).days
        if dias < 0:
            continue
        entry = mapa.setdefault(cat_id, {
            'nome': cat_nome,
            'horas_estimadas': horas_estimadas,
            'complexidade': complexidade,
            'dias': [],
        })
        entry['dias'].append(dias)
    resultado = sorted(
        [
            {
                'catalogo_id': cat_id,
                'catalogo_nome': data['nome'],
                'horas_estimadas': data['horas_estimadas'],
                'complexidade': data['complexidade'],
                'total_concluidos': len(data['dias']),
                'media_dias': round(sum(data['dias']) / len(data['dias']), 1),
            }
            for cat_id, data in mapa.items()
            if data['dias']
        ],
        key=lambda x: x['media_dias'],
        reverse=True,
    )
    return resultado


def _distribuicao_tempo_os(pares: list[tuple]) -> dict:
    buckets = {'ate_7': 0, 'de_8_a_15': 0, 'de_16_a_30': 0, 'de_31_a_60': 0, 'acima_60': 0}
    for criacao, fim in pares:
        if criacao and fim:
            dias = (fim - criacao).days
            if dias <= 7:
                buckets['ate_7'] += 1
            elif dias <= 15:
                buckets['de_8_a_15'] += 1
            elif dias <= 30:
                buckets['de_16_a_30'] += 1
            elif dias <= 60:
                buckets['de_31_a_60'] += 1
            else:
                buckets['acima_60'] += 1
    return buckets
