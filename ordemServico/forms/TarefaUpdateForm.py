from django.forms import ModelForm, Select
from django import forms
from ordemServico.models import Tarefa

class TarefaUpdateForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['status', 'data_inicio', 'data_termino']
        widgets = {
            'status': Select(attrs={
                'class': 'form-select w-100',
                'style': 'color: var(--cinza); font-size: 12px;'
            }),

            'data_inicio': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control w-100',
                'style': 'color: var(--cinza); font-size: 12px;'
            }),

            'data_termino': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control w-100',
                'style': 'color: var(--cinza); font-size: 12px;'
            }),
        }