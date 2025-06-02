from django.forms import Select, TextInput, DateInput
from django import forms
from ordemServico.models import OrdemServico

class OrdemServicoUpdateForm(forms.ModelForm):
    class Meta:
        model = OrdemServico
        fields = ['faturamento', 'data_faturamento', 'numero_nf']
        widgets = {
            'faturamento': Select(attrs={
                'class': 'form-select w-100', 
            }),
            'numero_nf': TextInput(attrs={
                'class': 'form-control w-100',
            }),
            'data_faturamento': DateInput(
                attrs={
                    'type': 'date',
                    'class': 'form-control w-100', 
                },
                format='%Y-%m-%d'
            ),
        }

    # Sobrescreve o método init para ajustar o formato da data
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.data_faturamento:
            self.fields['data_faturamento'].widget.attrs['value'] = self.instance.data_faturamento.strftime('%Y-%m-%d')

   
