from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Case, When, Value, IntegerField
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from django.utils.dateparse import parse_datetime

from ordemServico.models import Servico, Profile

from ordemServico.forms import ServicoUpdateForm, TarefaForm

def verificar_tipo_usuario(user):

    # Função que verifica se o usuário é 'Diretor', 'Administrativo' ou 'Líder Técnico'

    try:
        return user.profile.role in [1, 2, 3]
    except Profile.DoesNotExist:
        return False


@user_passes_test(verificar_tipo_usuario)
@login_required
def lista_servicos(request):
    # Ordena os serviços: "em espera" primeiro
    servicos = Servico.objects.annotate(
        prioridade=Case(
            When(status='em_espera', then=Value(1)),
            When(status='em_andamento', then=Value(2)),
            When(status='concluida', then=Value(3)),
            default=Value(4),
            output_field=IntegerField(),
        )
    ).order_by('prioridade', 'status')

    # Paginação: 20 serviços por página
    paginator = Paginator(servicos, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        data = [
            {
                "id": servico.id,
                "cliente_nome": servico.ordem_servico.cliente.nome.upper() if servico.ordem_servico and servico.ordem_servico.cliente else "N/A",
                "tipo_inscricao": servico.ordem_servico.cliente.tipo_inscricao if servico.ordem_servico and servico.ordem_servico.cliente else None,
                "tipo_inscricao_display": servico.ordem_servico.cliente.get_tipo_inscricao_display() if servico.ordem_servico and servico.ordem_servico.cliente else None,
                "numero_inscricao": servico.ordem_servico.cliente.numero_inscricao if servico.ordem_servico and servico.ordem_servico.cliente else "N/A",
                "tipo_cliente": servico.ordem_servico.cliente.tipo_cliente if servico.ordem_servico and servico.ordem_servico.cliente else None,
                "tipo_cliente_display": servico.ordem_servico.cliente.get_tipo_cliente_display() if servico.ordem_servico and servico.ordem_servico.cliente else None,
                "nome_representante": servico.ordem_servico.cliente.nome_representante if servico.ordem_servico and servico.ordem_servico.cliente else "Não cadastrado",
                "setor_representante": servico.ordem_servico.cliente.setor_representante if servico.ordem_servico and servico.ordem_servico.cliente else "Não cadastrado",
                "email_representante": servico.ordem_servico.cliente.email_representante if servico.ordem_servico and servico.ordem_servico.cliente else "Não cadastrado",
                "telefone_representante": servico.ordem_servico.cliente.contato_representante if servico.ordem_servico and servico.ordem_servico.cliente else "Não cadastrado",
                "ordem_servico_id": servico.ordem_servico.id if servico.ordem_servico else None,
                "valor": servico.ordem_servico.valor if servico.ordem_servico else None,
                "repositorio_nome": servico.repositorio.nome if servico.repositorio else "N/A",
                "status": servico.status,
                "status_display": servico.get_status_display(),
                "descricao": servico.descricao,
                "data_conclusao": servico.data_conclusao if servico.data_conclusao else "N/A",
                "form_status": {
                    "status": ServicoUpdateForm(instance=servico)['status'].as_widget(),
                    "data_conclusao": ServicoUpdateForm(instance=servico)['data_conclusao'].as_widget(),
                },
                "form_tarefa": {
                    "profile": TarefaForm()['profile'].as_widget(),
                    "descricao": TarefaForm()['descricao'].as_widget(),
                },
                "tarefas": [
                    {
                        "profile": str(tarefa.profile),
                        "descricao": tarefa.descricao,
                        "status": tarefa.get_status_display(),
                        "data_conclusao": tarefa.data_termino if tarefa.data_termino else "Não concluída",
                    }
                    for tarefa in servico.tarefas.all()
                ],
            }
            for servico in page_obj
        ]
        return JsonResponse({
            "servicos": data,
            "has_previous": page_obj.has_previous(),
            "has_next": page_obj.has_next(),
            "previous_page_number": page_obj.previous_page_number() if page_obj.has_previous() else None,
            "next_page_number": page_obj.next_page_number() if page_obj.has_next() else None,
            "current_page": page_obj.number,
            "total_pages": paginator.num_pages,
        })

    return render(request, "ordemServico/area_tecnica/servicos.html")


@login_required
@user_passes_test(verificar_tipo_usuario)
def atualizar_status_servico(request, servico_id):
    if request.method == "POST":
        servico = get_object_or_404(Servico, id=servico_id)
        form = ServicoUpdateForm(request.POST, instance=servico)

        if form.is_valid():
            servico = form.save()
            return JsonResponse({
                "success": True,
                "message": "Status atualizado com sucesso!",
                "status": servico.get_status_display(),
                "data_conclusao": servico.data_conclusao.strftime('%Y-%m-%d') if servico.data_conclusao else None
            })

        return JsonResponse({"success": False, "errors": form.errors.as_json()}, status=400)

    return JsonResponse({"success": False, "message": "Método inválido."}, status=405)



@login_required
@user_passes_test(verificar_tipo_usuario)
def adicionar_tarefa(request, servico_id):
    """Adiciona uma nova tarefa ao serviço."""
    if request.method == "POST":
        servico = get_object_or_404(Servico, id=servico_id)  
        form = TarefaForm(request.POST)
        if form.is_valid():
            tarefa = form.save(commit=False)
            tarefa.servico = servico 
            tarefa.save()

            # Substitua `data_conclusao` por `data_termino`
            data_termino = tarefa.data_termino.strftime('%Y-%m-%d') if tarefa.data_termino else None
            status = tarefa.get_status_display()

            return JsonResponse({
                "success": True,
                "tarefa": {
                    "id": tarefa.id,
                    "profile": str(tarefa.profile),
                    "descricao": tarefa.descricao,
                    "status": status,
                    "data_conclusao": data_termino  # Atualize para `data_termino`
                },
                "message": "Tarefa adicionada com sucesso!"
            })

        return JsonResponse({
            "success": False,
            "errors": form.errors.as_json()
        }, status=400)

    return JsonResponse({
        "success": False,
        "message": "Método inválido."
    }, status=405)
