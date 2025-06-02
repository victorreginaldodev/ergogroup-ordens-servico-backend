from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('ordemServico.urls.OrdemServicoUrls')),

    path('', include('ordemServico.urls.FinanceiroUrls')),

    path('', include('ordemServico.urls.ServicosUrls')),

    path('', include('ordemServico.urls.TarefasUrls')),

    path('', include('ordemServico.urls.OsRapidaUrls')),

    path('', include('ordemServico.urls.LoginUrls')),

    path('', include('ordemServico.urls.RegistroUrls')),

    path('', include('ordemServico.urls.ClientesUrls')),

    path('', include('ordemServico.urls.RepositorioUrls')),

    path('', include('ordemServico.urls.UsuarioUrls')),

    path('', include('ordemServico.urls.PainelControleUrls')),
    
    path('', include('ordemServico.urls.ApiUrls')),

] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)