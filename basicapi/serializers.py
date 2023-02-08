from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Profile

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('email', 'password', 'username', 'id', 'kaonavi_code')
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        return user

    def update(self, use_instance, validated_data):
        for attr, value in validated_data.items():
            if attr == 'password':
                use_instance.set_password(value)
            else:
                setattr(use_instance, attr, value)
        use_instance.save()
        return use_instance

class ProfileSerializer(serializers.ModelSerializer):

    created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)
    updated_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M:%S', read_only=True)

    class Meta:
        model = Profile
        fields = (
            'user', 'top_image', 'nickname', 'created_at', 'updated_at',
            'location','hobby', 'tweet', 'introduction'
        )
        extra_kwargs = {'user': {'read_only': True}}
