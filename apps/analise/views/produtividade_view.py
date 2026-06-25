from datetime import date, datetime, time

from django.db.models import Count, Max, Q
from django.db.models.functions import TruncMonth
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.analise.utils import gerar_intervalo_meses, preencher_meses
from apps.contas.models.choices import TipoUsuario
from apps.ordem_servico.models import OrdemServico
from apps.ordem_servico.models.ordem_servico import Status as StatusOS
from apps.servicos.models import Servico
from apps.servicos.models.servico import StatusServico
from apps.tarefas.models import Tarefa, MiniOS
from apps.tarefas.models.tarefa import StatusTarefa
from apps.tarefas.models.mini_os import StatusMiniOS


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
        os_concluidas = (
            OrdemServico.objects
            .filter(status=StatusOS.CONCLUIDA, data_criacao__gte=data_inicio)
            .annotate(
                data_fim_real=Max(
                    'servicos__data_termino',
                    filter=Q(servicos__status='concluida'),
                )
            )
            .filter(data_fim_real__isnull=False)
        )
        os_media = _media_dias(os_concluidas.values_list('data_criacao', 'data_fim_real'))

        servicos_concluidos = Servico.objects.filter(
            status=StatusServico.CONCLUIDA,
            data_inicio__isnull=False,
            data_termino__isnull=False,
            data_termino__gte=data_inicio,
        )
        servico_media = _media_dias(servicos_concluidos.values_list('data_inicio', 'data_termino'))

        tarefas_com_inicio = Tarefa.objects.filter(
            data_inicio__isnull=False,
            data_inicio__gte=data_inicio,
        )
        lead_time_media = _media_dias(
            (timezone.localtime(criada_em).date(), inicio)
            for inicio, criada_em in tarefas_com_inicio.values_list('data_inicio', 'criada_em')
        )

        return {
            'os_criacao_para_encerramento_dias': os_media,
            'servicos_inicio_para_fim_dias': servico_media,
            'tarefa_criacao_para_inicio_dias': lead_time_media,
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
        tarefas_concluidas_qs = Tarefa.objects.filter(
            status=StatusTarefa.CONCLUIDA,
            data_termino__isnull=False,
            data_termino__gte=data_inicio,
        )
        minios_concluidas_qs = MiniOS.objects.filter(
            status=StatusMiniOS.FINALIZADA,
            data_termino__isnull=False,
            data_termino__gte=data_inicio,
        )
        tarefas_abertas_qs = Tarefa.objects.filter(
            status__in=[StatusTarefa.ABERTA, StatusTarefa.EM_ANDAMENTO],
        )
        minios_abertas_qs = MiniOS.objects.filter(
            status__in=[StatusMiniOS.NAO_INICIADO, StatusMiniOS.EM_ANDAMENTO],
        )

        if usuario.tipo_usuario == TipoUsuario.TECNICO:
            tarefas_concluidas_qs = tarefas_concluidas_qs.filter(responsavel=usuario)
            minios_concluidas_qs = minios_concluidas_qs.filter(responsavel=usuario)
            tarefas_abertas_qs = tarefas_abertas_qs.filter(responsavel=usuario)
            minios_abertas_qs = minios_abertas_qs.filter(responsavel=usuario)

        dados = {}
        duracoes_por_tecnico = {}
        tarefas_concluidas_por_mes = _mapa_por_responsavel_e_mes(tarefas_concluidas_qs, 'data_termino')
        minios_concluidas_por_mes = _mapa_por_responsavel_e_mes(minios_concluidas_qs, 'data_termino')

        for responsavel_id, nome, inicio, termino in tarefas_concluidas_qs.values_list(
            'responsavel_id', 'responsavel__nome_completo', 'data_inicio', 'data_termino',
        ):
            entry = dados.setdefault(responsavel_id, _linha_tecnico(responsavel_id, nome))
            entry['tarefas_concluidas'] += 1
            if inicio and termino:
                duracoes_por_tecnico.setdefault(responsavel_id, []).append((termino - inicio).days)

        for responsavel_id, nome in minios_concluidas_qs.values_list('responsavel_id', 'responsavel__nome_completo'):
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

        for responsavel_id, entry in dados.items():
            duracoes = duracoes_por_tecnico.get(responsavel_id) or []
            entry['tempo_medio_tarefa_dias'] = (
                round(sum(duracoes) / len(duracoes), 1) if duracoes else None
            )
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
        'mini_os_concluidas': 0,
        'tarefas_em_aberto': 0,
        'mini_os_em_aberto': 0,
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


def _media_dias(pares_datas) -> float | None:
    diffs = [(fim - inicio).days for inicio, fim in pares_datas if inicio and fim]
    if not diffs:
        return None
    return round(sum(diffs) / len(diffs), 1)
