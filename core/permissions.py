from rest_framework.permissions import BasePermission
from authentication.models import CustomUser


class IsManager(BasePermission):
    message = 'You Aren\'t A Manager!'

    def has_permission(self, request, view):
        return request.user.role == 'M'


class IsEmployee(BasePermission):
    message = 'You Aren\'t An Employee!'

    def has_permission(self, request, view):
        return request.user.role == 'E'



class IsProfileCompleted(BasePermission):
    message = 'لطفا اطلاعات شخصی خود را تکمیل کنید.'

    def has_permission(self, request, view):
        return CustomUser.objects.get(username=request.user.username).is_completed()


class IsAdmin(BasePermission):
    message = "YOU ARE NOT ADMIN!"

    def has_permission(self, request, view):
        return request.user.is_superuser
