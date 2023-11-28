from rest_framework.permissions import BasePermission
from authentication.models import CustomUser
from rest_framework import permissions


class IsAdminOrManager(BasePermission):
    message = 'You Aren\'t Admin or Organization\'s Manager!'

    def has_permission(self, request, view):
        return request.user.role == 'A' or request.user.role == 'M'


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
        return request.user.role == 'A'


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Allow GET requests to all users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check if the user has the "isAdmin" permission
        return request.user and request.user.role == 'A'
