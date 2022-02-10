from django.urls import path, re_path
from rest_framework_jwt.views import obtain_jwt_token

from app.views import CourseListAPIView, CurrentUser, NewsListAPIView, \
    CourseDetailAPIView, StudentListAPIView, UserAPIView, CourseFile, FileListAPIView

urlpatterns = [
    path('login', obtain_jwt_token),
    path('courses/', CourseListAPIView.as_view()),
    path('courses/<int:course_id>/', CourseDetailAPIView.as_view()),
    path('user/', CurrentUser.as_view()),
    path('user/<int:user_id>/', UserAPIView.as_view()),
    path('user/students/', StudentListAPIView.as_view()),
    re_path(r'^news/$', NewsListAPIView.as_view()),
    re_path(r'^files/$', FileListAPIView.as_view()),
    path('files/<int:file_id>/', CourseFile.as_view()),
]
