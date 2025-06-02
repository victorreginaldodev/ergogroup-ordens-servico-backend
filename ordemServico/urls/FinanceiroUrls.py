from django.urls import path
from ordemServico.views.FinanceiroView import financeiro, salvar_ordem_servico, atualizar_contador_liberadas, faturar_os_rapida, salvar_os_rapida
urlpatterns = [
    path('financeiro/', financeiro, name='financeiro'),
    path("salvar-ordem-servico/", salvar_ordem_servico, name="salvar_ordem_servico"),
    path("atualizar-contador-liberadas/", atualizar_contador_liberadas, name="atualizar_contador_liberadas"),
    path('financeiro/osrapida/', faturar_os_rapida, name='faturar_os_rapida'),
    path("financeiro/salvar-osrapida/", salvar_os_rapida, name="salvar_os_rapida"),
]
