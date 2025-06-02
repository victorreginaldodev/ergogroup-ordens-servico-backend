from django.forms import Select, DateInput
from django import forms
from ordemServico.models import Servico

class ServicoUpdateForm(forms.ModelForm):

    class Meta:
        model = Servico
        fields = ['status', 'data_conclusao']
        widgets = {
            'status': Select(attrs={
                'class': 'form-select form-control w-100',
                'style': 'font-size: 12px; color: var(--cinza)'
            }),
            'data_conclusao': DateInput(attrs={
                'type': 'date',
                'class': 'form-control w-100',
                'style': 'font-size: 12px; color: var(--cinza)'
            }),
        }

    def clean_status(self):
        status = self.cleaned_data.get('status')
        valid_statuses = ['em_espera', 'em_andamento', 'concluida']

        # Validar se o status está vazio ou inválido
        if not status:
            raise forms.ValidationError('O status não pode ser vazio.')

        if status not in valid_statuses:
            raise forms.ValidationError('O status selecionado é inválido.')

        return status
        

