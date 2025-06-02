from django.urls import path
from ordemServico.views.area_tecnica.OsRapidaView import listar_os_rapidas, atualizar_mini_os, criar_os_rapida, editar_os_rapida

urlpatterns = [
    path('listar/osrapidas', listar_os_rapidas, name='os_rapida'),
    path('atualizar-mini-os/<int:mini_os_id>/', atualizar_mini_os, name='atualizar-mini-os'),
    path('criar/osrapida/', criar_os_rapida, name='criar_os_rapida'),
    path('editar_os_rapida/<int:os_rapida_id>/', editar_os_rapida, name='editar_os_rapida'),
]