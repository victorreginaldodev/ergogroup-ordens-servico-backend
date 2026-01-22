from rest_framework import serializers
from ordemServico.models import Tarefa, Profile, Servico, OrdemServico
from .ProfileSerializer import ProfileSerializer

class TarefaListSerializer(serializers.ModelSerializer):
    cliente_nome = serializers.CharField(source='servico.ordem_servico.cliente.nome', read_only=True)
    repositorio_nome = serializers.CharField(source='servico.repositorio.nome', read_only=True)
    usuario_nome = serializers.CharField(source='profile.user.username', read_only=True)
    servico_descricao = serializers.CharField(source='servico.descricao', read_only=True)

    class Meta:
        model = Tarefa
        fields = ['id', 'cliente_nome', 'repositorio_nome', 'usuario_nome', 'status', 'descricao', 'servico_descricao']

class TarefaDetailSerializer(serializers.ModelSerializer):
    cliente = serializers.SerializerMethodField()
    servico_info = serializers.SerializerMethodField()

    class Meta:
        model = Tarefa
        fields = ['id', 'descricao', 'data_inicio', 'data_termino', 'status', 'cliente', 'servico_info']

    def get_cliente(self, obj):
        if not obj.servico or not obj.servico.ordem_servico or not obj.servico.ordem_servico.cliente:
            return None
        cliente = obj.servico.ordem_servico.cliente
        return {
            "nome": cliente.nome,
            "representante": {
                "nome": cliente.nome_representante,
                "setor": cliente.setor_representante,
                "email": cliente.email_representante
            },
            "contato": cliente.contato_representante
        }

    def get_servico_info(self, obj):
        if not obj.servico:
            return None
        servico = obj.servico
        return {
            "descricao": servico.descricao,
            "nome_repositorio": servico.repositorio.nome if servico.repositorio else None,
            "status": servico.status
        }

class TarefaSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    profile_id = serializers.PrimaryKeyRelatedField(
        queryset=Profile.objects.all(), source='profile', write_only=True
    )
    servico_id = serializers.PrimaryKeyRelatedField(
        queryset=Servico.objects.all(), source='servico', write_only=True
    )
    # Optional: Read-only field for servico details if needed, or just ID
    # servico = ServicoSerializer(read_only=True) # avoiding circular import if possible

    class Meta:
        model = Tarefa
        fields = '__all__'
