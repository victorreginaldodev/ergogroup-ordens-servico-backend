from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ordemServico.models import MiniOS
from ordemServico.serializers.MiniOSSerializer import (
    MiniOSSerializer,
    MiniOSFaturamentoSerializer,
)

class MiniOSViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = MiniOS.objects.all()
    serializer_class = MiniOSSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = MiniOS.objects.all()

        if user.is_authenticated and hasattr(user, 'profile'):
            if user.profile.role == 5:  # Técnico
                queryset = queryset.filter(profile__user=user)
            elif user.profile.role == 6:  # Gestor Comercial
                # Mesma regra do técnico: vê apenas seus próprios minios
                queryset = queryset.filter(profile__user=user)

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
