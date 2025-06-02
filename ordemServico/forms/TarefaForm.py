from django.forms import ModelForm, Select, Textarea
from ordemServico.models import Tarefa, Profile

class TarefaForm(ModelForm):

    class Meta:
        model = Tarefa
        fields = ['profile', 'descricao']
        widgets = {
            'profile': Select(attrs={
                'class': 'form-select', 
                'aria-label': 'Selecione um colaborador'
            }),
            'descricao': Textarea(attrs={
                'class': 'form-control textarea-control w-100',
                'style': 'height: 150px',
                'placeholder': 'Descrição da tarefa',
                'rows': 3,  
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super(TarefaForm, self).__init__(*args, **kwargs)
        # Ordenar o campo 'profile' pelo nome de usuário relacionado em ordem alfabética
        self.fields['profile'].queryset = Profile.objects.order_by('user__username')
