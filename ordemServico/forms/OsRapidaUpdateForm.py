from django.forms import  Select, DateInput, TextInput
from django import forms
from ordemServico.models import MiniOS, Cliente, RepositorioMiniOS, Profile

class OsRapidaUpdateForm(forms.ModelForm):
    
    class Meta:
        model = MiniOS
        fields = ['status', 'data_inicio', 'data_termino']
        widgets = {
            'status': Select(attrs={
                'class': 'form-select w-100', 
                'style': 'font-size: 12px; color: var(--cinza)'
            }),
            'data_termino': DateInput(attrs={
                'type': 'date',
                'class': 'form-control w-100',
                'style': 'font-size: 12px; color: var(--cinza)'
            }),
        } 

class OsRapidaFullUpdateForm(forms.ModelForm):

    class Meta:
        model = MiniOS
        fields = ['cliente', 'servico', 'quantidade', 'profile', 'descricao', 'data_recebimento', 'data_inicio', 'data_termino', 'status']
        widgets = {
            'cliente': forms.Select(attrs={
                'class': 'form-select w-100',
                'style': 'font-size: 12px; color: var(--cinza)',
            }),
            'servico': forms.Select(attrs={
                'class': 'form-select w-100',
                'style': 'font-size: 12px; color: var(--cinza)',
            }),
            'quantidade': forms.NumberInput(attrs={
                'class': 'form-control w-25',
                'min': '1',
                'style': 'font-size: 12px; color: var(--cinza)',
            }),
            'profile': forms.Select(attrs={
                'class': 'form-select w-100',
                'style': 'font-size: 12px; color: var(--cinza)',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control w-100',
                'style': 'font-size: 12px; color: var(--cinza)',
                'rows': '4',
                'placeholder': 'Digite a descrição do serviço',
            }),
            'data_recebimento': forms.DateInput(attrs={
                'class': 'form-control w-100',
                'type': 'date',
                'style': 'font-size: 12px; color: var(--cinza)',
            }, format='%Y-%m-%d'),  # Ajusta o formato para o esperado pelo HTML5
            'data_inicio': forms.DateInput(attrs={
                'class': 'form-control w-100',
                'type': 'date',
                'style': 'font-size: 12px; color: var(--cinza)',
            }, format='%Y-%m-%d'),
            'data_termino': forms.DateInput(attrs={
                'class': 'form-control w-100',
                'type': 'date',
                'style': 'font-size: 12px; color: var(--cinza)',
            }, format='%Y-%m-%d'),
            'status': forms.Select(attrs={
                'class': 'form-select w-100',
                'style': 'font-size: 12px; color: var(--cinza)',
            }),
        }

    def __init__(self, *args, **kwargs):
        super(OsRapidaFullUpdateForm, self).__init__(*args, **kwargs)
        
        # Ordenar os clientes e serviços em ordem alfabética
        self.fields['cliente'].queryset = Cliente.objects.order_by('nome')
        self.fields['servico'].queryset = RepositorioMiniOS.objects.order_by('nome')
        self.fields['profile'].queryset = Profile.objects.order_by('user__username')
        
        # Ajustar os valores dos campos de data para o formato correto
        for field in ['data_recebimento', 'data_inicio', 'data_termino']:
            if self.instance and getattr(self.instance, field):
                self.fields[field].initial = getattr(self.instance, field).strftime('%Y-%m-%d')


class OsRapidaFaturamentoForm(forms.ModelForm):
    
    class Meta:
        model = MiniOS 
        fields = ['faturamento', 'n_nf']
        widgets = {
            'faturamento': forms.Select(attrs={
                'class': 'form-select w-100',
            }),
            'n_nf': TextInput(attrs={
                'class': 'form-control w-50',
            }),
        }
