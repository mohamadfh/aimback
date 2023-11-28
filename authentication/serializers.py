from rest_framework import serializers
from .models import CustomUser


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'username', 'password', 'role')

    def create(self, validated_data):
        user = CustomUser.objects.create(username=validated_data['username'],
                                         role=validated_data['role'],
                                         last_name=validated_data['last_name'],
                                         first_name=validated_data['first_name'],
                                         )
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserSafeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'username', 'role')


class ManagerSafeSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='manager.organization.name', read_only=True)

    class Meta:
        model = CustomUser
        fields = ('id', 'first_name', 'last_name', 'username', 'organization_name')
