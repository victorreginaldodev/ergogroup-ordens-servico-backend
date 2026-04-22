from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from legado.ordemServico.models import Profile

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Adicionar informações do usuário
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
        }

        # Tentar obter o profile do usuário
        try:
            profile = Profile.objects.get(user=self.user)
            data['profile'] = {
                'id': profile.id,
                'role': profile.get_role_display(),
                'active': profile.active,
            }
        except Profile.DoesNotExist:
            data['profile'] = None

        return data
