from rest_framework import viewsets
from legado.ordemServico.models import Profile
from legado.ordemServico.serializers.ProfileSerializer import ProfileSerializer

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

