import json
from collections import defaultdict

from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from .models import Question, Block, UserAnswer, Employee
from .serializers import QuestionSerializer, BlockSerializer, UserAnswerSubmitSerializer, OrganizationSerializer, \
    OrganizationDetailSerializer
from .serializers import BlockDetailSerializer
from .choices import ANSWER_CHOICE_TO_TEXT
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Count
from .choices import ANSWER_CHOICES
from .scoring import calculate_block_score, calculate_total_score
from .permissions import IsAdminOrReadOnly, IsEmployee, IsAdminOrManager, IsAdmin
from .models import Organization


#
# class QuestionView(generics.RetrieveUpdateDestroyAPIView,generics.ListAPIView):
#     serializer_class = QuestionSerializer
#     queryset = Question.objects.all()
#
#     # authentication_classes = [TokenAuthentication]
#     # permission_classes = [IsAuthenticated]
#
#     # def get_queryset(self):
#     #     block_number = self.kwargs.get('block_number')
#     #     if block_number is not None:
#     #         # Filter questions by block number if provided
#     #         queryset = Question.objects.filter(block=block_number)
#     #     else:
#     #         # Return all questions if no block number is provided
#     #         queryset = Question.objects.all()
#     #     return queryset
#     # def get_queryset(self):
#     #     block_number = self.request.query_params.get('block_number')
#     #
#     #     if block_number is not None:
#     #         # Filter questions by block number if provided
#     #         queryset = Question.objects.filter(block=block_number)
#     #     else:
#     #         # Return all questions if no block number is provided
#     #         queryset = Question.objects.all()
#     #
#     #     return queryset
#
#

#
# class QuestionListCreateView(generics.ListCreateAPIView):
#     queryset = Question.objects.all()
#     serializer_class = QuestionSerializer
#     # authentication_classes = [TokenAuthentication]
#     # permission_classes = [IsAuthenticated]
#
#
# class QuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Question.objects.all()
#     serializer_class = QuestionSerializer
#     # authentication_classes = [TokenAuthentication]
#     # permission_classes = [IsAuthenticated]
#
#
# class BlockListCreateView(generics.ListCreateAPIView):
#     queryset = Block.objects.all()
#     serializer_class = BlockSerializer
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#
# class BlockDetailView(generics.RetrieveUpdateDestroyAPIView):
#     queryset = Block.objects.all()
#     serializer_class = BlockSerializer
#     authentication_classes = [TokenAuthentication]
#     permission_classes = [IsAuthenticated]
#
#
# class BlockDetailWithQuestions(APIView):
#     # authentication_classes = [TokenAuthentication]
#     # permission_classes = [IsAuthenticated]
#
#     def get(self, request, pk):
#         try:
#             block = Block.objects.get(pk=pk)
#         except Block.DoesNotExist:
#             return Response({"detail": "Block not found"}, status=404)
#
#         serializer = BlockDetailSerializer(block)
#         return Response(serializer.data)


class QuestionAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk=None):
        if pk is None:
            # Retrieve a list of all questions
            questions = Question.objects.all()
            serializer = QuestionSerializer(questions, many=True)
            return Response(serializer.data)
        else:
            try:
                question = Question.objects.get(pk=pk)
            except Question.DoesNotExist:
                return Response({"detail": "question not found"}, status=404)

            serializer = QuestionSerializer(question)
            return Response(serializer.data)

    def post(self, request, pk):
        if request.user.role != 'A':
            return Response({"message": "permission denied"}, status=403)
        # Create a new question
        serializer = QuestionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if request.user.role != 'A':
            return Response({"message": "permission denied"}, status=403)
        # Update an existing question by PK
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"detail": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = QuestionSerializer(question, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.role != 'A':
            return Response({"message": "permission denied"}, status=403)
        # Delete an existing question by PK
        try:
            question = Question.objects.get(pk=pk)
        except Question.DoesNotExist:
            return Response({"detail": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        question.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class BlockAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrReadOnly]

    def get(self, request, pk=None):
        # Retrieve a list of all blocks
        if pk is None:
            blocks = Block.objects.all()
            serializer = BlockSerializer(blocks, many=True)
            return Response(serializer.data)
        else:
            try:
                block = Block.objects.get(pk=pk)
            except Block.DoesNotExist:
                return Response({"detail": "Block not found"}, status=404)

            serializer = BlockDetailSerializer(block)
            return Response(serializer.data)

    def post(self, request):
        if request.user.role != 'A':
            return Response({"message": "permission denied"}, status=403)
        serializer = BlockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if request.user.role != 'A':
            return Response({"message": "permission denied"}, status=403)
        try:
            block = Block.objects.get(pk=pk)
        except Block.DoesNotExist:
            return Response({"detail": "Block not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = BlockSerializer(block, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.role != 'A':
            return Response({"message": "permission denied"}, status=403)
        # Delete an existing block by PK
        try:
            block = Block.objects.get(pk=pk)
        except Block.DoesNotExist:
            return Response({"detail": "Block not found"}, status=status.HTTP_404_NOT_FOUND)

        block.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserAnswerSubmitView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsEmployee]

    def get(self, request):
        user = request.user.employee
        if user.has_submitted:
            return Response({"message": "Answers has been submitted successfully", "has_submitted": 1}, status=200)
        else:
            return Response({"message": "Answers has not been submitted", "has_submitted": 0}, status=200)

    def post(self, request):
        data = request.data["answers"]
        user = request.user.employee
        if user.has_submitted:
            return Response({"message": "You already submitted"}, status=400)
        user_answers = []
        for question_id, answer in data.items():
            try:
                question = Question.objects.get(pk=question_id)
            except Question.DoesNotExist:
                return Response({"message": f"Question with ID {question_id} not found"}, status=400)
            if answer > 5 or answer < 1:
                return Response({"message": f"invalid answer"}, status=400)

            user_answer = UserAnswer(user=user, question=question, answer=answer - 1)
            user_answers.append(user_answer)

        if len(user_answers) != Question.objects.count():
            return Response({"message": "All questions must be submitted"}, status=400)
        UserAnswer.objects.bulk_create(user_answers)
        user.has_submitted = True
        user.save()
        return Response({"message": "Answers submitted successfully"}, status=201)


class QuestionAnswerCountAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrManager]

    def get(self, request, pk=None, org_id=None):
        if request.user.role == 'M' and pk is not None:
            current_user_organization = request.user.manager.organization
            answer_counts = (
                UserAnswer.objects
                .filter(question_id=pk)
                .filter(user__organization=current_user_organization)
                .values('answer')
                .annotate(count=Count('id'))  # Count based on UserAnswer instances
            )
            response_data = {choice[0]: 0 for choice in ANSWER_CHOICES}

            for entry in answer_counts:
                response_data[entry['answer']] = entry['count']

            return Response(response_data)
        elif request.user.role == 'A' and org_id is not None and pk is not None:
            answer_counts = (
                UserAnswer.objects
                .filter(question_id=pk)
                .filter(user__organization__id=org_id)
                .values('answer')
                .annotate(count=Count('id'))  # Count based on UserAnswer instances
            )
            response_data = {choice[0]: 0 for choice in ANSWER_CHOICES}

            for entry in answer_counts:
                response_data[entry['answer']] = entry['count']
            return Response(response_data)
        return Response({}, status=400)


class BlockAnswerCountAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrManager]

    def get(self, request, pk, org_id=None):
        if request.user.role == 'M':
            current_user_organization = request.user.manager.organization
            block_reports = UserAnswer.objects \
                .filter(question__block__id=pk) \
                .filter(user__organization=current_user_organization) \
                .select_related('question_id').values(
                'question_id', 'answer', "question__text",
            ).annotate(count=Count("id"))
            result = defaultdict(lambda: {"answer_count": {choice[0]: 0 for choice in ANSWER_CHOICES}})
            for answer_count in block_reports:
                answer_count_dict = result[answer_count["question_id"]]["answer_count"]
                answer_count_dict[answer_count["answer"]] = answer_count["count"]
                result[answer_count["question_id"]] = {
                    "answer_count": answer_count_dict,
                    "text": answer_count["question__text"],
                }
            return Response(result)
        elif request.user.role == 'A' and org_id is not None:
            block_reports = UserAnswer.objects \
                .filter(question__block__id=pk) \
                .filter(user__organization__id=org_id) \
                .select_related('question_id').values(
                'question_id', 'answer', "question__text",
            ).annotate(count=Count("id"))
            result = defaultdict(lambda: {"answer_count": {choice[0]: 0 for choice in ANSWER_CHOICES}})
            for answer_count in block_reports:
                answer_count_dict = result[answer_count["question_id"]]["answer_count"]
                answer_count_dict[answer_count["answer"]] = answer_count["count"]
                result[answer_count["question_id"]] = {
                    "answer_count": answer_count_dict,
                    "text": answer_count["question__text"],
                }
            return Response(result)
        return Response({}, status=400)

        # result = {}
        # for q in questions:
        #     answer_counts = (
        #         UserAnswer.objects
        #         .filter(question=q)
        #         # .filter(user__organization=current_user_organization)
        #         .values('answer')
        #         .annotate(count=Count('id'))  # Count based on UserAnswer instances
        #     )
        #     response_data = {choice[0]: 0 for choice in ANSWER_CHOICES}
        #     for entry in answer_counts:
        #         response_data[entry['answer']] = entry['count']
        #     result[q.id] = {"answer_count" :response_data , "qid" : q.id , "text": q.text}
        # return Response(result)


class BlockScoreAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrManager]

    def get(self, request, pk, org_id=None):
        if request.user.role == 'M':
            current_user_organization = request.user.manager.organization
        elif request.user.role == 'A':
            current_user_organization = Organization.objects.get(pk=org_id)
        # Use aggregation to count selected answers for the specified question and answer choice
        current_user_organization = request.user.manager.organization
        answer_counts = (
            UserAnswer.objects
            .filter(question__block__id=pk)
            .filter(user__organization=current_user_organization)
            .values('answer')
            .annotate(count=Count('id'))  # Count based on UserAnswer instances
        )
        # Serialize the results
        response_data = {choice[0]: 0 for choice in ANSWER_CHOICES}

        for entry in answer_counts:
            response_data[entry['answer']] = entry['count']

        response_data = {"block": pk, "organization_id": current_user_organization.id,
                         "score": calculate_block_score(response_data)}
        return Response(response_data)


class TotalScoreAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrManager]

    def get(self, request, org_id=None):
        # Use aggregation to count selected answers for the specified question and answer choice
        if request.user.role == 'M':
            current_user_organization = request.user.manager.organization
        elif request.user.role == 'A':
            current_user_organization = Organization.objects.get(pk=org_id)
        block_score = {}
        for block in range(1, 10):
            answer_counts = (
                UserAnswer.objects
                .filter(question__block__id=block)
                .filter(user__organization=current_user_organization)
                .values('answer')
                .annotate(count=Count('id'))  # Count based on UserAnswer instances
            )
            # Serialize the results
            response_data = {choice[0]: 0 for choice in ANSWER_CHOICES}

            for entry in answer_counts:
                response_data[entry['answer']] = entry['count']
            block_score[block] = calculate_block_score(response_data)

        return Response({"organization_id": current_user_organization.id,
                         "totalscore": calculate_total_score(block_score)})


class GeneralReportAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrManager]

    def get(self, request, org_id=None):
        BLOCKS = [
            {
                "number": 1,
                "name": "جاه طلبی"
            },
            {
                "number": 2,
                "name": "موارد کاربردی"
            },
            {
                "number": 3,
                "name": "سازمان دهی"
            },
            {
                "number": 4,
                "name": "تخصص"
            },
            {
                "number": 5,
                "name": "فرهنگ سازمانی"
            },
            {
                "number": 6,
                "name": "فناوری"
            },
            {
                "number": 7,
                "name": "داده"
            },
            {
                "number": 8,
                "name": "اکوسیستم هوش مصنوعی"
            },
            {
                "number": 9,
                "name": "اجرا"
            }
        ]

        if request.user.role == 'M':
            current_user_organization = request.user.manager.organization
        elif request.user.role == 'A':
            current_user_organization = Organization.objects.get(pk=org_id)
        block_score = {}
        report = {"organization": current_user_organization.name}
        report['block_answer_count'] = []
        for block in range(1, 10):
            answer_counts = (
                UserAnswer.objects
                .filter(question__block__id=block)
                .filter(user__organization=current_user_organization)
                .values('answer')
                .annotate(count=Count('id'))  # Count based on UserAnswer instances
            )
            # Serialize the results
            response_data = {choice[0]: 0 for choice in ANSWER_CHOICES}

            for entry in answer_counts:
                response_data[entry['answer']] = entry['count']
            block_score[block] = calculate_block_score(response_data)
            BLOCKS[block - 1]['score'] = block_score[block]
            response_data = {ANSWER_CHOICE_TO_TEXT[c]: response_data[c] for c in response_data}
            response_data["موضوع"] = BLOCKS[block - 1]['name']
            report['block_answer_count'].append(response_data)

        report["block_score"] = BLOCKS
        report['total_score'] = calculate_total_score(block_score)

        question_instance = Question.objects.first()
        employee_count = Employee.objects.filter(organization=current_user_organization).count()
        submission_count = UserAnswer.objects.filter(user__organization=current_user_organization). \
            filter(question=question_instance).count()

        report['employee_count'] = employee_count
        report['submission_count'] = submission_count

        return Response(report)


class BlockreportAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrManager]

    def get(self, request, pk, org_id=None):
        # Use aggregation to count selected answers for the specified question and answer choice
        if request.user.role == 'M':
            current_user_organization = request.user.manager.organization
        elif request.user.role == 'A':
            current_user_organization = Organization.objects.get(pk=org_id)
        answer_counts = (
            UserAnswer.objects
            .filter(question__block__id=pk)
            .filter(user__organization=current_user_organization)
            .values('answer')
            .annotate(count=Count('id'))  # Count based on UserAnswer instances
        )
        # Serialize the results
        response_data = {choice[0]: 0 for choice in ANSWER_CHOICES}

        for entry in answer_counts:
            response_data[entry['answer']] = entry['count']

        response_data = {"block": pk, "score": calculate_block_score(response_data), "answer_counts": response_data}
        return Response(response_data)


class OrganizationAPIView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminOrManager]

    def get(self, request, pk=None):

        if pk is None and request.user.role == 'A':
            organizations = Organization.objects.all()
            serializer = OrganizationSerializer(organizations, many=True)
            return Response(serializer.data)
        elif pk is None and request.user.role == 'M':
            organization = request.user.manager.organization
            serializer = OrganizationDetailSerializer(organization)
            return Response(serializer.data)
        else:
            if request.user.role != 'A' and request.user.manager.organization.id != pk:
                return Response({"message": "permission denied"}, status=403)
            try:
                organization = Organization.objects.get(pk=pk)
            except Organization.DoesNotExist:
                return Response({"detail": "organization not found"}, status=404)
            serializer = OrganizationDetailSerializer(organization)
            return Response(serializer.data)

    def post(self, request, pk=None):
        if request.user.role != 'A':
            return Response({"message": "permission denied"}, status=403)
        serializer = OrganizationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        if request.user.role != 'A':
            return Response({"message": "permission denied"}, status=403)
        try:
            organization = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return Response({"detail": "organization not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = OrganizationSerializer(organization, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        if request.user.role != 'A':
            return Response({"message": "permission denied"}, status=403)
        try:
            organization = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return Response({"detail": "organization not found"}, status=status.HTTP_404_NOT_FOUND)

        organization.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
