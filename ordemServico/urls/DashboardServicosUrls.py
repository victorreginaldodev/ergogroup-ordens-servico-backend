from django.urls import path
from ordemServico.views.area_tecnica.DashboardServicosView import *

urlpatterns = [
    path('lider/dashboard/lider', dashborad_lider, name='dashboard_lider'),
    path('api/servicos-por-status/', servicos_por_status, name='servicos_por_status'),
    path('conclusao_servicos_por_mes/', conclusao_servicos_por_mes, name='conclusao_servicos_por_mes'),
    path('lista_profiles/', lista_profiles, name='lista_profiles'),
    path('tarefas_por_status/', tarefas_por_status, name='tarefas_por_status'), 
    path('tarefas_por_status/<int:profile_id>/', tarefas_por_status, name='tarefas_por_status_profile'), 
]
