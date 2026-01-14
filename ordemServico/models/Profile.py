from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class Profile(models.Model):

    TIPO_USUARIO = (
        (1, 'Diretor'),
        (2, 'Administrativo'),
        (3, 'Líder Técnico'),
        (4, 'Sub-Líder Técnico'),
        (5, 'Técnico'),
        (6, 'Gestor Comercial'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.IntegerField(choices=TIPO_USUARIO, default=5)
    created = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=True)


    def __str__(self):
        return self.user.username