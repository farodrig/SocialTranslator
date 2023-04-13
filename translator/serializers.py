from .models import Message
from rest_framework import serializers


class MessageSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if ("content" not in data or data['content'] == "") and ("file" not in data or data['file'] == ""):
            raise serializers.ValidationError("The message must have at least the field content or file")
        return data

    class Meta:
        model = Message
        fields = '__all__'

