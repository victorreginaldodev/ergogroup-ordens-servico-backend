from django.urls import path
from legado.ordemServico.views.RegistroView import register

urlpatterns = [
    path('registro/', register, name='registro'),
]
