from django.forms import ModelForm, Select, NumberInput, Textarea, DateInput
from ordemServico.models import MiniOS, Cliente, RepositorioMiniOS, Profile

class OsRapidaForm(ModelForm):
    
    class Meta:
        model = MiniOS
        fields = ['cliente', 'servico', 'quantidade', 'profile', 'descricao', 'data_recebimento']
        widgets = {
            'cliente': Select(attrs={
                'class': 'form-select form-control w-75', 
                'id': 'floatingSelect', 
                'aria-label': 'Selecione um cliente',
            }),
            'servico': Select(attrs={
                'class': 'form-select form-control w-75', 
                'id': 'floatingSelect', 
                'aria-label': 'Selecione um serviço',
            }),
            'quantidade': NumberInput(attrs={
                'class': 'form-control w-50',                
            }), 
            'profile': Select(attrs={
                'class': 'form-select form-control w-75', 
                'id': 'floatingSelect', 
                'aria-label': 'Selecione um perfil',
            }),
            'descricao': Textarea(attrs={
                'class': 'form-control textarea-control w-100',
                'style': 'height: 150px',
                'id': 'floatingTextarea2',
                'placeholder': 'Digite aqui as observações sobre esse serviço...',
                'rows': 8,
            }),
            'data_recebimento': DateInput(attrs={
                'type': 'date',
                'class': 'form-control w-75'
            }), 
        }
    
    def __init__(self, *args, **kwargs):
        super(OsRapidaForm, self).__init__(*args, **kwargs)
        self.fields['cliente'].queryset = Cliente.objects.order_by('nome')
        self.fields['servico'].queryset = RepositorioMiniOS.objects.order_by('nome')
        self.fields['profile'].queryset = Profile.objects.order_by('user__username')
