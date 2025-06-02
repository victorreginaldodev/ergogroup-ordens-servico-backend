from django.forms import ModelForm, TextInput, Select, Textarea, EmailInput, CheckboxInput
from ordemServico.models import Cliente

class ClienteForm(ModelForm):

    class Meta:
        model = Cliente
        fields = '__all__'

        widgets = {
            'nome': TextInput(attrs={
                'class': 'form-control w-100',
                'placeholder': 'Digite a razão social do cliente'
            }),
            'tipo_inscricao': Select(attrs={
                'class': 'form-select',
                'id': 'id_tipo_inscricao',
            }),
            'numero_inscricao': TextInput(attrs={
                'class': 'form-control w-75',
                'id': 'id_numero_inscricao'
            }),
            'ramo_atividade': TextInput(attrs={
                'class': 'form-control'
            }),
            'ramo_atividade_detalhado': TextInput(attrs={
                'class': 'form-control'
            }),
            'grau_risco': Select(attrs={
                'class': 'form-select'
            }),
            'tipo_cliente': Select(attrs={
                'class': 'form-select',
            }),
            'cnae': TextInput(attrs={
                'class': 'form-control'
            }),
            'observacao': Textarea(attrs={
                'class': 'form-control textarea-control w-100',
                'style': 'height: 150px',
                'id': 'floatingTextarea2',
                'placeholder': 'Digite aqui algumas observações importantes sobre esse cliente',
                'rows': 8,
            }),
            'nome_representante': TextInput(attrs={
                'class': 'form-control w-100',
                'placeholder': 'Digite o nome do representante do cliente',
            }),
            'setor_representante': TextInput(attrs={
                'class': 'form-control w-100',
                 'placeholder': 'Informe o setor do representante da empresa'
            }),
            'email_representante': EmailInput(attrs={
                'class': 'form-control w-100',
                'placeholder': 'Informe o e-mail do representante da empresa',
            }),
            'contato_representante': TextInput(attrs={
                'class': 'form-control w-100',
                'placeholder': 'Informe o contato do representante da empresa',
                'id': 'id_contato_representante',
            }),
            'cliente_ativo': Select(attrs={
                'class': 'form-select',
            }),
            'renovacao_automatica': CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_renovacao_automatica',
            }),
            'cobranca_revisao_alteracao': CheckboxInput(attrs={
                'class': 'form-check-input',
                'id': 'id_cobranca_revisao_alteracao',
            }),
        }