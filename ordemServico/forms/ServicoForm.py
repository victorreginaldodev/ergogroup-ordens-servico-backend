from django import forms
from ordemServico.models import Servico, Repositorio

class ServicoForm(forms.ModelForm):
    class Meta:
        model = Servico
        fields = ['repositorio', 'descricao'] 
        widgets = {
            'repositorio': forms.Select(attrs={
                'class': 'form-select w-50', 
                'id': 'floatingSelect',
                'aria-label': 'Selecione um repositório',
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control textarea-control w-100',
                'style': 'height: 150px',
                'id': 'floatingTextarea2',
                'placeholder': 'Digite aqui a descrição...',
                'rows': 8,
                'required': 'required',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(ServicoForm, self).__init__(*args, **kwargs)
        self.fields['repositorio'].queryset = Repositorio.objects.order_by('nome')
