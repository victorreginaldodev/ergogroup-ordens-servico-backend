from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, OuterRef, Subquery, Count, Q, F
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt

from ordemServico.models import OrdemServico, Profile, MiniOS, Servico
from ordemServico.forms import OrdemServicoUpdateForm, OsRapidaFaturamentoForm


def verificar_tipo_usuario(user):
    """
    Verifica se o usuário tem um papel permitido (Diretor, Administrativo ou Líder Técnico)
    """
    try:
        return user.profile.role in [1, 2, 3]
    except Profile.DoesNotExist:
        return False

@login_required
@user_passes_test(verificar_tipo_usuario)
def financeiro(request):
    todas_ordens = OrdemServico.objects.all()

    total_nao_liberadas = sum(
        ordem.valor for ordem in todas_ordens if not ordem.liberada_para_faturamento()
    )

    servicos_concluidos = Servico.objects.filter(
        ordem_servico=OuterRef('pk'),
        status='concluida'
    ).values('ordem_servico').annotate(count=Count('id')).values('count')

    total_servicos = Servico.objects.filter(
        ordem_servico=OuterRef('pk')
    ).values('ordem_servico').annotate(count=Count('id')).values('count')

    ordens_servicos = OrdemServico.objects.annotate(
        total_servicos=Subquery(total_servicos),
        servicos_concluidos=Subquery(servicos_concluidos)
    ).filter(
        total_servicos=F('servicos_concluidos')
    ).distinct()

    ordens_com_formularios = [
        {
            "ordem": ordem,
            "form": OrdemServicoUpdateForm(instance=ordem)
        }
        for ordem in ordens_servicos
    ]

    context = {
        "ordens_com_formularios": ordens_com_formularios,
        "total_faturadas": ordens_servicos.filter(faturamento="sim").aggregate(Sum("valor"))["valor__sum"] or 0,
        "total_liberadas": (
            ordens_servicos.filter(cobranca_imediata="sim", faturamento="nao") |
            ordens_servicos.filter(servicos__isnull=False, servicos__status="concluida")
            .exclude(faturamento="sim")
        ).distinct().aggregate(Sum("valor"))["valor__sum"] or 0,
        "total_nao_liberadas": total_nao_liberadas,
    }

    return render(request, "ordemServico/financeiro/financeiro.html", context)


@login_required
@user_passes_test(verificar_tipo_usuario)
@csrf_exempt
def salvar_ordem_servico(request):
    if request.method == "POST" and request.headers.get("X-Requested-With") == "XMLHttpRequest":
        ordem_id = request.POST.get("ordem_id")
        if not ordem_id:
            return JsonResponse({"success": False, "message": "ID da ordem não fornecido."}, status=400)

        ordem = get_object_or_404(OrdemServico, id=ordem_id)  # Garante que a ordem existe
        form = OrdemServicoUpdateForm(request.POST, instance=ordem)

        if form.is_valid():
            form.save()  # Salva os dados no banco
            return JsonResponse({"success": True, "message": "Dados salvos com sucesso!"})
        else:
            return JsonResponse({
                "success": False,
                "errors": form.errors.as_json()
            }, status=400)

    return JsonResponse({"success": False, "message": "Requisição inválida."}, status=400)


@login_required
@user_passes_test(verificar_tipo_usuario)
def atualizar_contador_liberadas(request):
    if request.method == "GET" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        # Itera sobre todas as ordens e conta as liberadas para faturamento e não faturadas
        total_liberadas = sum(
            1 for ordem in OrdemServico.objects.filter(faturamento="nao")
            if ordem.liberada_para_faturamento()
        )

        return JsonResponse({"total_liberadas": total_liberadas})

    return JsonResponse({"error": "Requisição inválida."}, status=400)


@login_required
@user_passes_test(verificar_tipo_usuario)
def faturar_os_rapida(request):
    # Filtrar MiniOS pelo nome do serviço contendo "CORREÇÃO CLIENTE"
    # e clientes com "cobranca_revisao_alteracao=True"
    os_rapidas = MiniOS.objects.filter(
        servico__nome__icontains="CORREÇÃO CLIENTE",  # Filtra pelo nome do serviço
        cliente__cobranca_revisao_alteracao=True  # Verifica se o cliente cobra revisões
    )

    # Associar formulários a cada MiniOS
    os_rapidas_com_formularios = [
        {
            "os_rapida": os_rapida,
            "form": OsRapidaFaturamentoForm(instance=os_rapida)
        }
        for os_rapida in os_rapidas
    ]

    # Contexto para o template
    context = {
        "os_rapidas_com_formularios": os_rapidas_com_formularios,
    }

    return render(request, "ordemServico/financeiro/financeiro_os_rapidas.html", context)

@csrf_exempt
def salvar_os_rapida(request):
    if request.method == "POST" and request.headers.get("x-requested-with") == "XMLHttpRequest":
        os_rapida_id = request.POST.get("minios_id")
        os_rapida = get_object_or_404(MiniOS, id=os_rapida_id)

        form = OsRapidaFaturamentoForm(request.POST, instance=os_rapida)
        if form.is_valid():
            form.save()
            return JsonResponse({
                "success": True,
                "message": "Faturamento da ordem de serviço rápida feito com sucesso!",
                "faturamento": os_rapida.faturamento,  # Retorna o estado atualizado
            })
        else:
            return JsonResponse({
                "success": False,
                "message": "Erro ao salvar MiniOS.",
                "errors": form.errors.as_json(),
            }, status=400)

    return JsonResponse({"success": False, "message": "Requisição inválida."}, status=400)
