from django.urls import path
from ordemServico.views.LoginView import user_login, user_logout

urlpatterns = [
    path('', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]