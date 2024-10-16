from django.forms import ModelForm, Select, DateInput
from django import forms
from ordemServico.models import Tarefa

class TarefaUpdateForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = ['status', 'data_inicio', 'data_termino']
        widgets = {
            'status': Select(attrs={
                'class': 'form-select form-control w-100',
            }),

            'data_inicio': forms.DateInput(attrs={
                'type': 'date',
            }),

            'data_termino': forms.DateInput(attrs={
                'type': 'date',
            }),
        }