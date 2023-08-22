from rest_framework import serializers
from .models import Question


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'  # You can specify fields explicitly if needed

    def create(self, validated_data):
        c = Question.objects.create(**validated_data)
        c.save()
        return c
