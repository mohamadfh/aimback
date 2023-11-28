from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from .views import QuestionAPIView, BlockAPIView ,QuestionAnswerCountAPIView , BlockScoreAPIView,\
    UserAnswerSubmitView , TotalScoreAPIView , GeneralReportAPIView , BlockreportAPIView , BlockAnswerCountAPIView,OrganizationAPIView

urlpatterns = [
    path('submitbulk/', UserAnswerSubmitView.as_view(), name='submit'),
    path('questions/<int:pk>/count', QuestionAnswerCountAPIView.as_view(), name='question-answer-report'),
    path('questions/<int:pk>/count/<int:org_id>/', QuestionAnswerCountAPIView.as_view(), name='question-answer-report'),
    path('questions/', QuestionAPIView.as_view(), name='question-list'),
    path('questions/<int:pk>', QuestionAPIView.as_view(), name='question-detail'),
    path('blocks/', BlockAPIView.as_view(), name='block-list'),
    path('blocks/<int:pk>/', BlockAPIView.as_view(), name='block-detail'),
    path('blocks/<int:pk>/report', BlockreportAPIView.as_view(), name='block-report'),
    path('blocks/<int:pk>/report/<int:org_id>/', BlockreportAPIView.as_view(), name='block-report'),
    path('blocks/<int:pk>/count/<int:org_id>/', BlockAnswerCountAPIView.as_view(), name='block-answer-count'),
    path('blocks/<int:pk>/count', BlockAnswerCountAPIView.as_view(), name='block-answer-count'),
    path('totalscore', TotalScoreAPIView.as_view(), name='total score'),
    path('organizations/report/<int:org_id>/', GeneralReportAPIView.as_view(), name='general-report'),
    path('organizations/report', GeneralReportAPIView.as_view(), name='general-report'),
    path('organizations/', OrganizationAPIView.as_view(), name='organization-list'),
    path('organizations/<int:pk>/', OrganizationAPIView.as_view(), name='organization-detail'),

]