from django.contrib.auth.models import User
from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        #extra_kwargs = {'password' : { 'write-only': True }}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)    
        return user

class SongSerializer(serializers.ModelSerializer):
    class Meta:
        model = Song
        fields = ['id', 'file', 'embedding', 'uploaded_at' ]
        read_only_fields = ['embedding', 'uploaded_at']    