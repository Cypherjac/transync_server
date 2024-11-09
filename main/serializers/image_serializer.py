from rest_framework import serializers

class ImageSerializer(serializers.Serializer):
    imageFile = serializers.ImageField()
