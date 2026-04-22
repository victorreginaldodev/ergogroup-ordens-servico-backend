from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('legado.ordemServico.urls.OrdemServicoUrls')),

    path('', include('legado.ordemServico.urls.FinanceiroUrls')),

    path('', include('legado.ordemServico.urls.ServicosUrls')),

    path('', include('legado.ordemServico.urls.TarefasUrls')),

    path('', include('legado.ordemServico.urls.OsRapidaUrls')),

    path('', include('legado.ordemServico.urls.LoginUrls')),

    path('', include('legado.ordemServico.urls.RegistroUrls')),

    path('', include('legado.ordemServico.urls.ClientesUrls')),

    path('', include('legado.ordemServico.urls.RepositorioUrls')),

    path('', include('legado.ordemServico.urls.UsuarioUrls')),

    path('', include('legado.ordemServico.urls.PainelControleUrls')),

    path('', include('legado.ordemServico.urls.ApiUrls')),

    path('api/contas/', include('apps.contas.urls')),
    path('api/clientes/', include('apps.clientes.urls')),
    path('api/ordem-servico/', include('apps.ordem_servico.urls')),
    path('api/servicos/', include('apps.servicos.urls')),
    path('api/tarefas/', include('apps.tarefas.urls')),
    path('api/analise/', include('apps.analise.urls')),

    # Documentação da API
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)