from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import Employee, Manager
# from StudyArena.models import Student, Teacher
from .serializers import UserSerializer, UserSafeSerializer, ManagerSafeSerializer
from .models import CustomUser
# import utils
from core.models import Organization
from core.permissions import IsManager, IsAdmin


class SignUp(APIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def post(self, request):
        data = {'username': request.data['username'],
                'password': request.data['password'],
                }
        if 'admin' in request.data['role']:
            data['role'] = 'A'
        if 'manager' in request.data['role']:
            data['role'] = 'M'
        if 'employee' in request.data['role']:
            data['role'] = 'E'
        user = UserSerializer(data=data)
        if user.is_valid():
            user = user.save()
            return Response({
                'id': user.id,
                'is_signed_up': True,
                'message': 'OK',
            }, status=200)
        return Response({'is_signed_up': False,
                         'is_logged_in': False,
                         'token': '',
                         'message': user.errors,
                         }, status=403)


class RegisterUser(APIView):
    serializer_class = UserSerializer
    permission_classes = (IsManager,)

    def get_complete_role(self, role):
        if role == 'M':
            return 'manager'
        if role == 'A':
            return 'admin'
        if role == 'E':
            return 'employee'
        return "unknown"

    def post(self, request):
        current_user_organization = request.user.manager.organization
        data = {'username': request.data['username'], 'password': request.data['password'],
                'organization': current_user_organization.id, 'first_name': request.data['first_name'],
                'last_name': request.data['last_name'], 'role': 'E'}

        # if 'manager' == request.data['role']:
        #     data['role'] = 'M'
        # if 'employee' == request.data['role']:
        user = UserSerializer(data=data)
        if user.is_valid():
            user = user.save()
            print(user.last_name)
            if data['role'] == 'M':
                Manager.objects.create(user=user, organization=current_user_organization)
            elif data['role'] == 'E':
                Employee.objects.create(user=user, organization=current_user_organization)
            return Response({
                'id': user.id,
                'is_signed_up': True,
                'message': 'OK',
            }, status=200)
        return Response({'is_signed_up': False,
                         'message': user.errors,
                         }, status=403)

    def get(self, request, pk=None):
        current_user_organization = request.user.manager.organization

        if pk is None:
            # Retrieve a list of all questions

            employee_users = CustomUser.objects.filter(role='E').filter(
                employee__organization=current_user_organization)
            serializer = UserSafeSerializer(employee_users, many=True)
            return Response(serializer.data)
        else:
            try:
                employee_user = CustomUser.objects.get(pk=pk)
            except CustomUser.DoesNotExist:
                return Response({"detail": "user not found"}, status=404)

            serializer = UserSafeSerializer(employee_user)
            return Response(serializer.data)

    def delete(self, request, pk):
        user = get_object_or_404(CustomUser, id=pk)
        if user.employee.organization != request.user.manager.organization:
            return Response({
                'message': 'you are not allowed to delete this user.',
            }, status=403)

        user.delete()
        return Response({
            'message': 'user deleted',
            'id': request.user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
        }, status=200)

    def put(self, request, pk):
        user = get_object_or_404(CustomUser, id=pk)
        if user.employee.organization != request.user.manager.organization:
            return Response({
                'message': 'you are not allowed to edit this user.',
            }, status=403)
        user_serializer = UserSerializer(instance=user, data={k: v for k, v in request.data.items() if k != 'role'},
                                         partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({
                'message': 'user data updated!',
                'id': request.user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'role': self.get_complete_role(user.role),
            }, status=200)
        return Response({
            'message': 'something is wrong!',
            'errors': user_serializer.errors
        }, status=400)


class RegisterManager(APIView):
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)

    def get_complete_role(self, role):
        if role == 'M':
            return 'manager'
        if role == 'A':
            return 'admin'
        if role == 'E':
            return 'employee'
        return "unknown"

    def get(self, request):
        managers = CustomUser.objects.filter(role='M')
        serializer = ManagerSafeSerializer(managers, many=True)
        return Response(serializer.data)

    def post(self, request):

        data = {'username': request.data['username'], 'password': request.data['password'],
                'organization': request.data['organization'], 'role': 'M',
                'first_name': request.data['first_name'],
                'last_name': request.data['last_name']}

        user = UserSerializer(data=data)
        organization_object = Organization.objects.get(name=data.get("organization"))

        if user.is_valid():
            user = user.save()

            Manager.objects.create(user=user, organization=organization_object)
            return Response({
                'id': user.id,
                'is_signed_up': True,
                'message': 'OK',
            }, status=200)
        return Response({'is_signed_up': False,
                         'token': '',
                         'message': user.errors,
                         }, status=403)

    def put(self, request, pk):
        user = get_object_or_404(CustomUser, id=pk)
        user_serializer = UserSerializer(instance=user, data={k: v for k, v in request.data.items() if k != 'role'},
                                         partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({
                'message': 'user data updated!',
                'id': request.user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'role': self.get_complete_role(user.role),
            }, status=200)
        return Response({
            'message': 'something is wrong!',
            'errors': user_serializer.errors
        }, status=400)

    def delete(self, request, pk):
        user = get_object_or_404(CustomUser, id=pk)
        user.delete()
        return Response(status=204)


class CustomLogin(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        user = self.serializer_class(data=request.data)
        if user.is_valid():
            validated_user = user.validated_data['user']
            tk, created = Token.objects.get_or_create(user=validated_user)
            return Response(data={
                'id': validated_user.pk,
                'token': tk.key,
            }, status=200)
        return Response(data={
            'id': 'null',
            'token': 'null',
        }, status=400)


class Profile(APIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_complete_role(self, role):
        if role == 'M':
            return 'manager'
        if role == 'A':
            return 'admin'
        if role == 'E':
            return 'employee'
        return "unknown"

    def get(self, request, **kwargs):
        user = get_object_or_404(CustomUser, username=request.user.username)
        filter_option = kwargs.get('filter_option', 'all')
        if filter_option == 'role':
            return Response({
                'id': user.id,
                'role': 'manager' if user.role == 'M' else (
                    'admin' if user.role == 'A' else 'employee' if user.role == 'E' else 'unknown'),
            }, status=200)
        return Response({
            'id': user.id,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'username': user.username,
            'role': self.get_complete_role(user.role),
        }, status=200)

    def put(self, request):
        user = get_object_or_404(CustomUser, username=request.user.username)
        user_serializer = UserSerializer(instance=user, data={k: v for k, v in request.data.items() if k != 'role'},
                                         partial=True)
        if user_serializer.is_valid():
            user_serializer.save()
            return Response({
                'message': 'user data updated!',
                'id': request.user.id,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'username': user.username,
                'role': self.get_complete_role(user.role),
            }, status=200)
        return Response({
            'message': 'something is wrong!',
            'errors': user_serializer.errors
        }, status=400)


class Logout(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        token = get_object_or_404(Token, user=request.user)
        token.delete()
        return Response({'message': 'logged out successfully.'}, status=200)
