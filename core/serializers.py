from rest_framework import serializers

class API_Image_Handle(serializers.Serializer):
    image = serializers.FileField()


