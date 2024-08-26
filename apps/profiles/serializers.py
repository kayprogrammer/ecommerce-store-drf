from rest_framework import serializers


class ProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=25)
    last_name = serializers.CharField(max_length=25)
    email = serializers.CharField(read_only=True)
    avatar_url = serializers.CharField(read_only=True)
    avatar = serializers.ImageField(write_only=True)
    account_type = serializers.CharField(read_only=True)
