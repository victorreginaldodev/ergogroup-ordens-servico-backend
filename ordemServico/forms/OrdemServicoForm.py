from django.forms import ModelForm, Select, TextInput, DateInput, EmailInput, Textarea
from django import forms
from ordemServico.models import OrdemServico, Cliente  # Assumindo que Cliente é o modelo relacionado

class OrdemServicoForm(ModelForm):
    
    class Meta:
        model = OrdemServico
        exclude = ['usuario_criador', 'concluida', 'faturamento', 'numero_nf', 'data_faturamento']
        widgets = {
            'cliente': Select(attrs={
                'class': 'form-select w-100', 
                'id': 'floatingSelect', 
                'aria-label': 'Selecione um cliente',
            }),
            'valor': TextInput(attrs={
                'class': 'form-control w-100', 
                'id': 'valorInput',
                'aria-label': 'Valor',
                'placeholder': 'R$ 00,00',
                'required': True
            }),
            'cobranca_imediata': Select(attrs={
                'class': 'form-select w-100', 
                'id': 'floatingSelect', 
                'aria-label': 'Cobrar imediatamente?',
            }),
            'forma_pagamento': Select(attrs={
                'class': 'form-select w-100', 
                'id': 'floatingSelect', 
                'aria-label': 'Forma de pagamento',
            }),
            'quantidade_parcelas': Select(attrs={
                'class': 'form-select  w-100', 
                'id': 'floatingSelect', 
                'aria-label': 'Quantidade de parcelas',
            }),
            'faturamento_1': DateInput(attrs={
                'class': 'form-control w-100', 
                'id': 'faturamento_1', 
                'placeholder': 'Selecione a data', 
                'type': 'date',
            }, format='%Y-%m-%d'
            ),
            'nome_contato_envio_nf': TextInput(attrs={
                'class': 'form-control',
                'id': 'floatingInput',
            }),
            'contato_envio_nf': EmailInput(attrs={
                'class': 'form-control',
                'id': 'emailInput',
            }),
            'observacao': Textarea(attrs={
                'class': 'form-control textarea-control w-100',
                'style': 'height: 150px',
                'id': 'floatingTextarea2',
                'placeholder': 'Digite aqui as observações sobre o pagamento para a equipe financeira...',
                'rows': 8,
            }),
            'data_criacao': DateInput(attrs={
                'class': 'form-control w-100', 
                'type': 'date',
            }, format='%Y-%m-%d'
            ),
        }

    def __init__(self, *args, **kwargs):
        super(OrdemServicoForm, self).__init__(*args, **kwargs)
        # Ordenar o queryset do cliente em ordem alfabética sem nenhum filtro
        self.fields['cliente'].queryset = Cliente.objects.order_by('nome')

