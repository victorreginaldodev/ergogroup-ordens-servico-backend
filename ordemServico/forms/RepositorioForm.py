from django.forms import ModelForm, TextInput, Textarea
from ordemServico.models import Repositorio

class RepositorioForm(ModelForm):

    class Meta:
        model = Repositorio
        fields = '__all__'
        widgets = {
            'nome': TextInput(attrs={
                'class': 'form-control w-100',
                'placeholder': 'Digite o nome do serviço'
            }),
            'descricao': Textarea(attrs={
                'class': 'form-control textarea-control w-100',
                'style': 'height: 150px',
                'id': 'floatingTextarea2',
                'placeholder': 'Digite uma descrição para o serviço',
                'rows': 8,
            }),
        }