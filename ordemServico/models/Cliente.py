from django.db import models

class Cliente(models.Model):

    TIPO_CLIENTE = (
        ('gestao', 'Gestão'),
        ('avulso', 'Avulso'),
        ('fornecedor', 'Fornecedor')
    )

    TIPO_INSCRICAO = (
        ('cnpj', 'CNPJ'),
        ('cpf', 'CPF'),
        ('cei', 'CEI'),
        ('cno', 'CNO'),
        ('caepf', 'CAEPF'),
    )

    CLIENTE_ATIVO = (
        ('sim', 'SIM'),
        ('nao', 'NÃO'),
    )

    nome = models.CharField(max_length=100, null=False, blank=False)
    tipo_inscricao = models.CharField(max_length=10, choices=TIPO_INSCRICAO, default='cnpj', null=True, blank=True)
    numero_inscricao = models.CharField(max_length=30, null=True, blank=True)
    tipo_cliente = models.CharField(choices=TIPO_CLIENTE, default='gestao', max_length=10, null=True, blank=True)
    observacao = models.TextField(null=True, blank=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    nome_representante = models.CharField(max_length=50, null=True, blank=True)
    setor_representante = models.CharField(max_length=50, null=True, blank=True)
    email_representante = models.EmailField(null=True, blank=True)
    contato_representante = models.CharField(max_length=50, null=True, blank=True)
    cliente_ativo = models.CharField(null=True, blank=True, max_length=5, choices=CLIENTE_ATIVO, default='sim')

    renovacao_automatica = models.BooleanField(default=False)
    cobranca_revisao_alteracao = models.BooleanField(default=True)

    def __str__(self):
        return self.nome