from rest_framework import serializers
from .models import Question, Block, Organization, Employee
from authentication.serializers import UserSerializer, UserSafeSerializer


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'  # You can specify fields explicitly if needed


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'  # You can specify fields explicitly if needed


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSafeSerializer()  # Serialize the associated user using UserSerializer

    class Meta:
        model = Employee
        fields = ('id', 'user')  # Include other fields from Employee if needed


class OrganizationDetailSerializer(serializers.ModelSerializer):
    employees = EmployeeSerializer(many=True, source='employee_set')

    class Meta:
        model = Organization
        fields = ('id', 'name', 'employees')


class BlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Block
        fields = '__all__'


class BlockDetailSerializer(serializers.ModelSerializer):
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Block
        fields = ['title', 'number', 'description', 'questions']

    def get_questions(self, obj):
        # Retrieve and serialize the questions associated with the block
        questions = Question.objects.filter(block=obj)
        serializer = QuestionSerializer(questions, many=True)
        return serializer.data


class UserAnswerSubmitSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    answer = serializers.IntegerField()
