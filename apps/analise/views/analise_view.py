from datetime import date, datetime

from django.db.models import Count, Max, Sum, Subquery, OuterRef
from django.db.models.functions import ExtractYear, ExtractMonth
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.analise.serializers import AnaliseDadosResponseSerializer
from apps.contas.permissions import usuario_pode_ver_valores
from apps.ordens_servico.models import OrdemServico
from apps.ordens_servico.models import Servico
from apps.ordens_servico.models.servico import StatusServico
from apps.ordens_servico.models import Tarefa, OrdemServicoOperacional
from apps.ordens_servico.models.tarefa import StatusTarefa
from apps.ordens_servico.models.ordem_servico_operacional import StatusOrdemServicoOperacional

from apps.analise.utils import agregar_por_mes, gerar_intervalo_meses, preencher_meses


class AnaliseDadosView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary='Análise de dados',
        description=(
            'Métricas agregadas dos últimos 12 meses: ordens de serviço, '
            'serviços, tarefas, ordens de serviço operacionais e clientes.\n\n'
            'Os campos `ordens_servico.vendas_por_mes` e o bloco `clientes` '
            'envolvem valores monetários e são omitidos da resposta para os '
            'perfis Sub-Líder Técnico, Técnico, Gestor Administrativo e '
            'Administrativo.'
        ),
        responses={200: AnaliseDadosResponseSerializer},
    )
    def get(self, request):
        hoje = timezone.now().date()
        meses = gerar_intervalo_meses(hoje, 12)
        data_inicio = date(meses[0]['ano'], meses[0]['mes'], 1)
        pode_ver_valores = usuario_pode_ver_valores(request.user)

        resultado = {
            'ordens_servico': self._ordens_servico(data_inicio, meses, pode_ver_valores, hoje),
            'servicos': self._servicos(data_inicio, meses),
            'tarefas': self._tarefas(data_inicio, meses),
            'minios': self._ordens_servico_operacionais(data_inicio, meses, hoje),
        }
        if pode_ver_valores:
            resultado['clientes'] = self._clientes()
        return Response(resultado)

    # ------------------------------------------------------------------ #

    def _ordens_servico(self, data_inicio, meses, pode_ver_valores, hoje):
        qs = OrdemServico.objects.all()

        mes_atual_inicio = date(hoje.year, hoje.month, 1)
        if hoje.month == 1:
            mes_anterior_inicio = date(hoje.year - 1, 12, 1)
        else:
            mes_anterior_inicio = date(hoje.year, hoje.month - 1, 1)

        abertas_map = agregar_por_mes(
            qs.filter(data_venda__gte=data_inicio),
            campo_data='data_venda',
        )
        ultimo_servico_data = (
            Servico.objects
            .filter(ordem_servico=OuterRef('pk'), status=StatusServico.CONCLUIDA, data_termino__isnull=False)
            .values('ordem_servico')
            .annotate(max_data=Max('data_termino'))
            .values('max_data')[:1]
        )
        concluidas_qs = (
            qs.filter(concluida=True)
            .annotate(data_conclusao=Subquery(ultimo_servico_data))
        )
        concluidas_com_data = concluidas_qs.filter(data_conclusao__isnull=False)
        concluidas_map = {
            date(item['ano'], item['mes'], 1): item['total']
            for item in (
                concluidas_com_data
                .annotate(
                    ano=ExtractYear('data_conclusao'),
                    mes=ExtractMonth('data_conclusao'),
                )
                .values('ano', 'mes')
                .annotate(total=Count('id'))
            )
        }

        resultado = {
            'total': qs.count(),
            'total_concluidas': qs.filter(concluida=True).count(),
            'total_nao_concluidas': qs.filter(concluida=False).count(),
            'abertas_por_mes': preencher_meses(meses, abertas_map),
            'concluidas_por_mes': preencher_meses(meses, concluidas_map),
            'abertas_mes_atual': qs.filter(data_venda__gte=mes_atual_inicio).count(),
            'abertas_mes_anterior': qs.filter(
                data_venda__gte=mes_anterior_inicio,
                data_venda__lt=mes_atual_inicio,
            ).count(),
            'concluidas_mes_atual': concluidas_com_data.filter(
                data_conclusao__gte=mes_atual_inicio,
            ).count(),
            'concluidas_mes_anterior': concluidas_com_data.filter(
                data_conclusao__gte=mes_anterior_inicio,
                data_conclusao__lt=mes_atual_inicio,
            ).count(),
            'em_aberto': qs.exclude(status__in=['concluida', 'cancelada']).count(),
        }

        if pode_ver_valores:
            vendas_map = agregar_por_mes(
                qs.filter(data_venda__gte=data_inicio),
                campo_data='data_venda',
                agregacao=Sum('valor'),
            )
            resultado['vendas_por_mes'] = preencher_meses(meses, vendas_map, default=0)
        return resultado

    def _servicos(self, data_inicio, meses):
        concluidos = Servico.objects.filter(
            status=StatusServico.CONCLUIDA,
            data_termino__isnull=False,
            data_termino__gte=data_inicio,
        )
        por_mes_map = agregar_por_mes(concluidos, campo_data='data_termino')
        principais = list(
            Servico.objects
            .filter(catalogo__isnull=False)
            .values('catalogo_id', 'catalogo__nome')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        por_status = [
            {
                'status': item['status'],
                'status_display': dict(StatusServico.choices).get(item['status'], item['status']),
                'total': item['total'],
            }
            for item in Servico.objects.values('status').annotate(total=Count('id'))
        ]
        return {
            'concluidos_ultimos_12_meses_total': concluidos.count(),
            'concluidos_por_mes': preencher_meses(meses, por_mes_map),
            'principais_por_quantidade': [
                {
                    'catalogo_id': i['catalogo_id'],
                    'catalogo_nome': i['catalogo__nome'],
                    'total': i['total'],
                }
                for i in principais
            ],
            'por_status': por_status,
        }

    def _tarefas(self, data_inicio, meses):
        concluidas = Tarefa.objects.filter(
            status=StatusTarefa.CONCLUIDA,
            data_termino__isnull=False,
            data_termino__gte=data_inicio,
        )
        por_mes_map = agregar_por_mes(concluidas, campo_data='data_termino')
        por_status = [
            {
                'status': item['status'],
                'status_display': dict(StatusTarefa.choices).get(item['status'], item['status']),
                'total': item['total'],
            }
            for item in Tarefa.objects.values('status').annotate(total=Count('id'))
        ]
        return {
            'por_status': por_status,
            'concluidas_por_mes': preencher_meses(meses, por_mes_map),
        }

    def _ordens_servico_operacionais(self, data_inicio, meses, hoje):
        qs = OrdemServicoOperacional.objects.all()

        mes_atual_inicio = date(hoje.year, hoje.month, 1)
        if hoje.month == 1:
            mes_anterior_inicio = date(hoje.year - 1, 12, 1)
        else:
            mes_anterior_inicio = date(hoje.year, hoje.month - 1, 1)

        # criada_em é DateTimeField: usa make_aware para o filtro e TruncMonth + .date()
        # para a chave do mapa, pois TruncMonth em DateTimeField retorna datetime (não date)
        # e preencher_meses espera date(ano, mes, 1) como chave.
        _aware = lambda d: timezone.make_aware(datetime(d.year, d.month, d.day))

        # MySQL sem timezone tables instaladas retorna NULL em CONVERT_TZ(), quebrando
        # ExtractYear/Month e TruncMonth em DateTimeField. Agrega em Python para evitar
        # qualquer função de timezone no banco.
        criadas_map: dict[date, int] = {}
        for dt in qs.filter(criada_em__gte=_aware(data_inicio)).values_list('criada_em', flat=True):
            local_dt = timezone.localtime(dt)
            key = date(local_dt.year, local_dt.month, 1)
            criadas_map[key] = criadas_map.get(key, 0) + 1

        # data_termino é DateField → agregar_por_mes funciona diretamente
        finalizadas_qs = qs.filter(
            status=StatusOrdemServicoOperacional.FINALIZADA,
            data_termino__isnull=False,
            data_termino__gte=data_inicio,
        )
        finalizadas_map = agregar_por_mes(finalizadas_qs, campo_data='data_termino')

        revisoes_qs = qs.filter(revisao_cliente=True, cliente__isnull=False)
        revisoes_por_cliente = [
            {
                'cliente_id': i['cliente_id'],
                'cliente_nome': i['cliente__nome'],
                'total': i['total'],
            }
            for i in (
                revisoes_qs
                .values('cliente_id', 'cliente__nome')
                .annotate(total=Count('id'))
                .order_by('-total')[:10]
            )
        ]

        return {
            'total': qs.count(),
            'total_revisao_cliente': qs.filter(revisao_cliente=True).count(),
            'criadas_por_mes': preencher_meses(meses, criadas_map),
            'finalizadas_por_mes': preencher_meses(meses, finalizadas_map),
            'criadas_mes_atual': qs.filter(criada_em__gte=_aware(mes_atual_inicio)).count(),
            'criadas_mes_anterior': qs.filter(
                criada_em__gte=_aware(mes_anterior_inicio),
                criada_em__lt=_aware(mes_atual_inicio),
            ).count(),
            'finalizadas_mes_atual': finalizadas_qs.filter(data_termino__gte=mes_atual_inicio).count(),
            'finalizadas_mes_anterior': finalizadas_qs.filter(
                data_termino__gte=mes_anterior_inicio,
                data_termino__lt=mes_atual_inicio,
            ).count(),
            'revisoes_por_cliente': revisoes_por_cliente,
        }

    def _clientes(self):
        mais_cobranca = [
            {
                'cliente_id': i['cliente_id'],
                'cliente_nome': i['cliente__nome'],
                'total_valor_cobrado': i['total'] or 0,
            }
            for i in (
                OrdemServico.objects.filter(cobranca_realizada=True)
                .values('cliente_id', 'cliente__nome')
                .annotate(total=Sum('valor'))
                .order_by('-total')[:5]
            )
            if i['cliente_id'] is not None
        ]
        mais_vendas = [
            {
                'cliente_id': i['cliente_id'],
                'cliente_nome': i['cliente__nome'],
                'total_valor_vendas': i['total'] or 0,
            }
            for i in (
                OrdemServico.objects
                .values('cliente_id', 'cliente__nome')
                .annotate(total=Sum('valor'))
                .order_by('-total')[:10]
            )
            if i['cliente_id'] is not None
        ]
        return {'mais_cobranca': mais_cobranca, 'mais_vendas': mais_vendas}
