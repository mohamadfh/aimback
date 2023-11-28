from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import RegisterUser, CustomLogin, Logout , Profile ,RegisterManager , SignUp

urlpatterns = [
    path('login/', CustomLogin.as_view()),
    path('register/', RegisterUser.as_view()),
    path('register/<int:pk>/', RegisterUser.as_view()),
    path('register/manager/', RegisterManager.as_view()),
    path('register/manager/<int:pk>/', RegisterManager.as_view()),
    path('whoami/', Profile.as_view()),
    path('whoami/<str:filter_option>/', Profile.as_view()),
    path('logout/', Logout.as_view()),
    # path('addadmin/', SignUp.as_view()),
]
