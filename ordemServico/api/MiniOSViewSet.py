from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ordemServico.models import MiniOS
from ordemServico.serializers.MiniOSSerializer import (
    MiniOSFaturamentoSerializer,
    MiniOSSerializer,
)

from .pagination import OptionalPageNumberPagination


class MiniOSViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = MiniOS.objects.all()
    serializer_class = MiniOSSerializer
    pagination_class = OptionalPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        queryset = MiniOS.objects.all()

        if user.is_authenticated and hasattr(user, 'profile'):
            if user.profile.role == 5:
                queryset = queryset.filter(profile__user=user)
            elif user.profile.role == 6:
                queryset = queryset.filter(profile__user=user)

        if self.action == 'list':
            q = self.request.query_params.get('q', '').strip()
            status = self.request.query_params.get('status', '').strip()

            if q:
                queryset = queryset.filter(
                    Q(cliente__nome__icontains=q)
                    | Q(servico__nome__icontains=q)
                    | Q(descricao__icontains=q)
                )

            if status:
                status_map = {
                    'pending': 'nao_iniciado',
                    'in_progress': 'em_andamento',
                    'completed': 'finalizada',
                }
                queryset = queryset.filter(status=status_map.get(status, status))

            queryset = queryset.select_related('cliente', 'servico', 'profile').order_by('status', '-id')

        return queryset

    @staticmethod
    def _usuario_pode_faturar(user):
        return (
            user.is_authenticated
            and hasattr(user, 'profile')
            and user.profile.role in [1, 2, 3]
        )

    @staticmethod
    def _os_rapidas_queryset():
        return MiniOS.objects.filter(
            servico__nome__icontains="CORREÇÃO CLIENTE",
            cliente__cobranca_revisao_alteracao=True,
        ).select_related('cliente', 'servico', 'profile')

    @action(detail=False, methods=['get'], url_path='os-rapidas')
    def os_rapidas(self, request):
        if not self._usuario_pode_faturar(request.user):
            return Response(
                {'detail': 'Você não tem permissão para acessar este recurso.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        queryset = self._os_rapidas_queryset()
        q = request.query_params.get('q', '').strip()
        billing_filter = request.query_params.get('billing', '').strip()

        if q:
            queryset = queryset.filter(
                Q(cliente__nome__icontains=q) | Q(id__icontains=q)
            )

        if billing_filter == 'faturada':
            queryset = queryset.filter(faturamento='sim')
        elif billing_filter == 'nao_faturada':
            queryset = queryset.filter(faturamento='nao')
        else:
            queryset = queryset.filter(faturamento__in=['sim', 'nao'])

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = MiniOSSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = MiniOSSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='faturar')
    def faturar(self, request, pk=None):
        if not self._usuario_pode_faturar(request.user):
            return Response(
                {'detail': 'Você não tem permissão para acessar este recurso.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        mini_os = self.get_object()

        if not self._os_rapidas_queryset().filter(pk=mini_os.pk).exists():
            return Response(
                {'detail': 'MiniOS não disponível para faturamento rápido.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MiniOSFaturamentoSerializer(
            mini_os, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
