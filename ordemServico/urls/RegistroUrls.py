from django.urls import path
from ordemServico.views.RegistroView import register

urlpatterns = [
    path('registro/', register, name='registro'),
]
