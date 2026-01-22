from rest_framework import serializers
from ordemServico.models import Servico, Repositorio, Tarefa, Profile, Cliente, OrdemServico
from .RepositorioSerializer import RepositorioSerializer

class ProfileInServicoSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username')

    class Meta:
        model = Profile
        fields = ['user_name', 'role']

class TarefaInServicoSerializer(serializers.ModelSerializer):
    profile = ProfileInServicoSerializer()

    class Meta:
        model = Tarefa
        fields = ['id', 'data_inicio', 'data_termino', 'status', 'profile', 'descricao']

class RepositorioListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repositorio
        fields = ['nome']

class ServicoListSerializer(serializers.ModelSerializer):
    repositorio = RepositorioListSerializer(read_only=True)
    cliente_nome = serializers.CharField(source='ordem_servico.cliente.nome', read_only=True)
    tem_tarefas = serializers.SerializerMethodField()

    class Meta:
        model = Servico
        fields = ['id', 'ordem_servico', 'cliente_nome', 'repositorio', 'status', 'tem_tarefas']

    def get_tem_tarefas(self, obj):
        # Optimization: use annotated value if available
        if hasattr(obj, 'has_tarefas'):
            return obj.has_tarefas
        # Fallback: Explicit query to ensure accuracy
        from ordemServico.models import Tarefa
        return Tarefa.objects.filter(servico_id=obj.id).exists()

class ClienteDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields = ['nome', 'nome_representante', 'setor_representante', 'email_representante', 'contato_representante']

class OrdemServicoDetailSerializer(serializers.ModelSerializer):
    cliente = ClienteDetailSerializer(read_only=True)

    class Meta:
        model = OrdemServico
        fields = ['id', 'valor', 'concluida', 'cliente']

class ServicoSerializer(serializers.ModelSerializer):
    tarefas = TarefaInServicoSerializer(many=True, read_only=True)
    repositorio = RepositorioSerializer(read_only=True)
    repositorio_id = serializers.PrimaryKeyRelatedField(
        queryset=Repositorio.objects.all(), source='repositorio', write_only=True, required=False, allow_null=True
    )
    ordem_servico_detail = OrdemServicoDetailSerializer(source='ordem_servico', read_only=True)
    ordem_servico = serializers.PrimaryKeyRelatedField(queryset=OrdemServico.objects.all(), write_only=True, required=False)

    class Meta:
        model = Servico
        fields = ['id', 'repositorio', 'repositorio_id', 'descricao', 'tarefas', 'status', 'data_conclusao', 'ordem_servico', 'ordem_servico_detail']
