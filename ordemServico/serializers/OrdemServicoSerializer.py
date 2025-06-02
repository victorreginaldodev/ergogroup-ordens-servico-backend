from rest_framework import serializers
from ordemServico.models import OrdemServico, Cliente, Servico, Repositorio, Tarefa, Profile


class ProfileOrdemServicoSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username')

    class Meta:
        model = Profile
        fields = ['user_name', 'role']


class TarefaSerializer(serializers.ModelSerializer):
    profile = ProfileOrdemServicoSerializer()

    class Meta:
        model = Tarefa
        fields = ['data_inicio', 'data_termino', 'status', 'profile']


class RepositorioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Repositorio
        fields = ['nome']


class ServicoSerializer(serializers.ModelSerializer):
    tarefas = TarefaSerializer(many=True, read_only=True,)
    repositorio = RepositorioSerializer()

    class Meta:
        model = Servico
        fields = ['repositorio', 'tarefas', 'status', 'data_conclusao']


class ClienteOrdemServicoSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cliente
        fields = ['nome', 'tipo_cliente', 'cliente_ativo']


class OrdemServicoSerializer(serializers.ModelSerializer):
    servicos = ServicoSerializer(many=True, read_only=True)
    cliente = ClienteOrdemServicoSerializer()

    class Meta:
        model = OrdemServico
        fields = '__all__'