from django.db import models
from django.contrib.auth.models import AbstractUser
from .choices import TipoUsuario


class Usuario(AbstractUser):
    email = models.EmailField(unique=True)
    nome_completo = models.CharField(max_length=255)
    tipo_usuario = models.CharField(max_length=30, choices=TipoUsuario.choices, default=TipoUsuario.ADMINISTRATIVO)
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'nome_completo']

    def __str__(self):
        return self.email