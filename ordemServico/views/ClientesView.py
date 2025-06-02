from django.shortcuts import render, redirect , get_object_or_404
from ordemServico.forms import ClienteForm

from django.contrib.auth.decorators import login_required, user_passes_test
from ordemServico.models import Profile, Cliente

def verificar_tipo_usuario(user):
    '''
      Função que verifica se o usuário é 'Diretor', 'Administrativo' ou 'Líder Técnico' 
    '''
    try:
        return user.profile.role in [1, 2, 3]
    except Profile.DoesNotExist:
        return False


@login_required
@user_passes_test(verificar_tipo_usuario)
def listar_clientes(request):
    clientes = Cliente.objects.all().order_by('nome')

    context = {
        'clientes': clientes
    }

    return render(request, 'ordemServico/clientes/listar_clientes.html', context)


@login_required
@user_passes_test(verificar_tipo_usuario)
def criar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('listar_clientes') 
    else:
        form = ClienteForm()  

    return render(request, 'ordemServico/clientes/criar_editar_cliente.html', {'form': form})


@login_required
@user_passes_test(verificar_tipo_usuario)
def editar_cliente(request, cliente_id):
    cliente = get_object_or_404(Cliente, id=cliente_id)  # Busca o cliente pelo ID

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)  # Preenche o formulário com os dados enviados
        if form.is_valid():
            form.save()  # Salva as alterações no banco de dados
            return redirect('listar_clientes')  # Redireciona para a lista de clientes
    else:
        form = ClienteForm(instance=cliente)  # Preenche o formulário com os dados do cliente

    context = {
        'form': form,
        'cliente': cliente
    }

    return render(request, 'ordemServico/clientes/criar_editar_cliente.html', context)
