from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Case, When, Value, IntegerField, Q
from ordemServico.models import Tarefa
from ordemServico.forms import TarefaUpdateForm
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime

@login_required
def tecnico(request):
    # Obtem o perfil do usuário logado
    user_profile = request.user.profile
    pesquisa = request.GET.get('pesquisa', '').strip().lower()
    status = request.GET.get('status', '').strip()

    # Filtra as tarefas relacionadas ao usuário logado
    tarefas = (
        Tarefa.objects.filter(profile=user_profile)
        .select_related('servico', 'ordem_servico')
        .annotate(
            status_priority=Case(
                When(status='nao_iniciada', then=Value(1)),
                When(status='em_andamento', then=Value(2)),
                When(status='concluida', then=Value(3)),
                default=Value(4),
                output_field=IntegerField(),
            )
        )
        .order_by('status_priority', 'data_inicio')  # Ordena pelo status personalizado e pela data de início
    )

    # Filtro de pesquisa
    if pesquisa:
        tarefas = tarefas.filter(
            Q(servico__ordem_servico__cliente__nome__icontains=pesquisa) |
            Q(servico__repositorio__nome__icontains=pesquisa)
        )

    # Filtro de status
    if status and status != 'todos':
        tarefas = tarefas.filter(status=status)

    # Ordena tarefas por prioridade de status e data de início
    tarefas = tarefas.order_by('status_priority', 'data_inicio')

    # Paginação: 20 tarefas por página
    paginator = Paginator(tarefas, 20)  
    page_number = request.GET.get('page', 1)  # Obtém o número da página
    page_obj = paginator.get_page(page_number)

    # Prepara os dados para retornar no formato JSON
    tarefas_data = [
        {
            "id": tarefa.id,
            "cliente": tarefa.servico.ordem_servico.cliente.nome,
            "tipo_inscricao": tarefa.servico.ordem_servico.cliente.get_tipo_inscricao_display(),
            "numero_inscricao": tarefa.servico.ordem_servico.cliente.numero_inscricao,
            "tipo_cliente": tarefa.servico.ordem_servico.cliente.get_tipo_cliente_display(),
            "nome_representante": tarefa.servico.ordem_servico.cliente.nome_representante,
            "setor_representante": tarefa.servico.ordem_servico.cliente.setor_representante,
            "email_representante": tarefa.servico.ordem_servico.cliente.email_representante,
            "telefone_representante": tarefa.servico.ordem_servico.cliente.contato_representante,
            "servico_nome": tarefa.servico.repositorio.nome if tarefa.servico else "Não informado",
            "ordem_servico_id": tarefa.ordem_servico.id if tarefa.ordem_servico else None,
            "descricao_tarefa": tarefa.descricao if tarefa.descricao else "Descrição para a tarefa não informada",
            "descricao_servico": tarefa.servico.descricao if tarefa.servico.descricao else "Descrição do serviço não informado",
            "data_inicio": tarefa.data_inicio.strftime('%Y-%m-%d') if tarefa.data_inicio else None,
            "data_termino": tarefa.data_termino.strftime('%Y-%m-%d') if tarefa.data_termino else None,
            "status": tarefa.get_status_display(),
            "form_update": {
                "status": TarefaUpdateForm(instance=tarefa)['status'].as_widget(),
                "data_inicio": TarefaUpdateForm(instance=tarefa)['data_inicio'].as_widget(),
                "data_termino": TarefaUpdateForm(instance=tarefa)['data_termino'].as_widget(),
            },
        }
        for tarefa in page_obj
    ]

    # Verifica se é uma requisição AJAX para retornar JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            "tarefas": tarefas_data,
            "has_previous": page_obj.has_previous(),
            "has_next": page_obj.has_next(),
            "previous_page_number": page_obj.previous_page_number() if page_obj.has_previous() else None,
            "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
        })

    # Caso não seja AJAX, renderiza o template com as tarefas
    return render(
        request, 
        'ordemServico/area_tecnica/tarefas.html', 
        {"tarefas": page_obj}
    )


@csrf_exempt
@require_POST
def atualizar_tarefa(request, tarefa_id):
    try:
        tarefa = Tarefa.objects.get(id=tarefa_id)
        
        # Obtém os valores enviados no POST
        status = request.POST.get('status')
        data_inicio = request.POST.get('data_inicio')
        data_termino = request.POST.get('data_termino')

        # Converte strings para objetos `date`, se possível
        tarefa.status = status
        tarefa.data_inicio = datetime.strptime(data_inicio, '%Y-%m-%d').date() if data_inicio else None
        tarefa.data_termino = datetime.strptime(data_termino, '%Y-%m-%d').date() if data_termino else None

        tarefa.save()

        return JsonResponse({
            "success": True,
            "tarefa": {
                "id": tarefa.id,
                "status": tarefa.get_status_display(),
                "data_inicio": tarefa.data_inicio.strftime('%Y-%m-%d') if tarefa.data_inicio else None,
                "data_termino": tarefa.data_termino.strftime('%Y-%m-%d') if tarefa.data_termino else None,
            },
        })

    except Tarefa.DoesNotExist:
        return JsonResponse({"success": False, "error": "Tarefa não encontrada"}, status=404)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)