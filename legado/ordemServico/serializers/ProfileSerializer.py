from rest_framework import serializers
from django.contrib.auth.models import User
from legado.ordemServico.models import Profile

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {
            'username': {'validators': []},
        }

class ProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    role_display = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ['id', 'user', 'role', 'role_display', 'created', 'active']

    def get_role_display(self, obj):
        return obj.get_role_display()

    def validate(self, attrs):
        user_data = attrs.get('user')
        if user_data:
            username = user_data.get('username')
            if self.instance:  # Update
                if username and username != self.instance.user.username:
                    if User.objects.filter(username=username).exists():
                        raise serializers.ValidationError({"user": {"username": ["Um usuário com este nome de usuário já existe."]}})
            else:  # Create
                if username:
                    if User.objects.filter(username=username).exists():
                        raise serializers.ValidationError({"user": {"username": ["Um usuário com este nome de usuário já existe."]}})
        return attrs

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = user_data.pop('password', None)

        user = User.objects.create(**user_data)
        if password:
            user.set_password(password)
            user.save()

        profile = Profile.objects.create(user=user, **validated_data)
        return profile

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)

        if user_data:
            user = instance.user
            password = user_data.pop('password', None)

            for attr, value in user_data.items():
                setattr(user, attr, value)

            if password:
                user.set_password(password)

            user.save()

        return super().update(instance, validated_data)
