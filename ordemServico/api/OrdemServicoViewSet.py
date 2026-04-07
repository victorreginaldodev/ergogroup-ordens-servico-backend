from django.db.models import Count, F, OuterRef, Q, Subquery
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from ordemServico.models import OrdemServico, Servico
from ordemServico.serializers import (
    OrdemServicoFaturamentoSerializer,
    OrdemServicoListSerializer,
    OrdemServicoSerializer,
)

from .pagination import OptionalPageNumberPagination


class OrdemServicoViewSet(viewsets.ModelViewSet):
    queryset = OrdemServico.objects.select_related("cliente")
    pagination_class = OptionalPageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset().select_related("cliente")

        if self.action == 'list':
            q = self.request.query_params.get('q', '').strip()
            date_from = self.request.query_params.get('date_from', '').strip()
            date_to = self.request.query_params.get('date_to', '').strip()

            if q:
                queryset = queryset.filter(cliente__nome__icontains=q)
            if date_from:
                queryset = queryset.filter(data_criacao__gte=date_from)
            if date_to:
                queryset = queryset.filter(data_criacao__lte=date_to)

            queryset = queryset.order_by('-data_criacao', '-id')

        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return OrdemServicoListSerializer
        if self.action == 'faturamento':
            return OrdemServicoFaturamentoSerializer
        return OrdemServicoSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(usuario_criador=self.request.user.username)
        else:
            serializer.save()

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except ValidationError as e:
            print("\n\n========== ORDEM SERVICO UPDATE ERROR ==========")
            print(f"Request Data: {request.data}")
            print(f"Error Details: {e.detail}")
            print("================================================\n\n")
            raise e

    @action(detail=False, methods=['get'], url_path='faturamento')
    def faturamento(self, request):
        q = request.query_params.get('q', '').strip()
        status_filter = request.query_params.get('status', '').strip()
        billing_filter = request.query_params.get('billing', '').strip()

        servicos_concluidos_subquery = (
            Servico.objects.filter(
                ordem_servico=OuterRef('pk'),
                status='concluida',
            )
            .values('ordem_servico')
            .annotate(count=Count('id'))
            .values('count')
        )

        total_servicos_subquery = (
            Servico.objects.filter(
                ordem_servico=OuterRef('pk'),
            )
            .values('ordem_servico')
            .annotate(count=Count('id'))
            .values('count')
        )

        annotated = self.get_queryset().annotate(
            total_servicos=Subquery(total_servicos_subquery),
            servicos_concluidos=Subquery(servicos_concluidos_subquery),
        )

        queryset = (
            annotated.filter(
                Q(cobranca_imediata='sim')
                | Q(
                    servicos__isnull=False,
                    total_servicos=F('servicos_concluidos'),
                )
            )
            .distinct()
        )

        if q:
            queryset = queryset.filter(
                Q(cliente__nome__icontains=q) | Q(id__icontains=q)
            )

        if status_filter == 'concluida':
            queryset = queryset.filter(
                Q(cobranca_imediata='sim') | Q(concluida='sim')
            )
        elif status_filter == 'andamento':
            queryset = queryset.filter(
                Q(cobranca_imediata='sim') | ~Q(concluida='sim')
            )

        if billing_filter == 'faturada':
            queryset = queryset.filter(faturamento='sim')
        elif billing_filter == 'nao_faturada':
            queryset = queryset.filter(faturamento='nao')
        elif billing_filter == 'all':
            queryset = queryset.filter(faturamento__in=['sim', 'nao'])
        else:
            queryset = queryset.filter(faturamento='nao')

        queryset = (
            queryset
            .filter(
                Q(faturamento='sim') | Q(faturamento='nao')
            )
            .distinct()
        )
        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
