from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView

from app.filters import NewsFilter, FileFilter
from app.models import Course, News, File, User
from app.permissions import IsTeacherOrStudent
from app.serializers import CourseSerializer, UserSerializer, NewsSerializer, FileSerializer


class CourseListAPIView(APIView):
    @classmethod
    def get(cls, request):
        if request.user.is_student:
            serializer = CourseSerializer(request.user.accessed_courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.user.is_teacher:
            serializer = CourseSerializer(request.user.courses, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)

    @classmethod
    def post(cls, request):
        if request.user.is_teacher:
            serializer = CourseSerializer(data=request.data, context={"user": request.user})
            if serializer.is_valid():
                serializer.save()
                course = Course.objects.get(id=serializer.data.get('id'))
                course.students.set(User.objects.filter(id__in=request.data.get('students') or []))
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_403_FORBIDDEN)


class StudentListAPIView(APIView):
    @classmethod
    def get(cls, request):
        if request.user.is_teacher:
            students = User.objects.filter(type=1)
            serializer = UserSerializer(students, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)


class NewsListAPIView(generics.ListCreateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = NewsFilter


class CurrentUser(APIView):
    @classmethod
    def get(cls, request):
        return Response(UserSerializer(request.user).data, status=status.HTTP_200_OK)

    @classmethod
    def put(cls, request):
        form = PasswordChangeForm(request.user, request.data)
        if form.is_valid():
            serializer = UserSerializer(instance=request.user, data=request.data)
            if serializer.is_valid():
                serializer.save()
                user = form.save()
                update_session_auth_hash(request, user)  # Important!
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(form.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CourseDetailAPIView(APIView):
    @classmethod
    def get(cls, request, course_id):
        course = Course.objects.filter(id=course_id)
        if course.exists():
            serializer = CourseSerializer(course[0])
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class UserAPIView(APIView):
    @classmethod
    def get(cls, request, user_id):
        user = User.objects.filter(id=user_id)
        if user.exists():
            serializer = UserSerializer(user[0])
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)


class FileListAPIView(generics.ListCreateAPIView):
    serializer_class = FileSerializer
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (IsTeacherOrStudent,)
    filter_class = FileFilter

    def get_queryset(self):
        if self.request.user.is_student:
            return self.request.user.accessed_files
        elif self.request.user.is_teacher:
            return self.request.user.files

    def perform_create(self, serializer):
        if not self.request.user.is_teacher:
            raise PermissionError('Only teachers can create files')

        serializer.save()
        file = File.objects.get(id=serializer.data.get('id'))
        file.students.set(User.objects.filter(id__in=self.request.data.get('students')))


class CourseFile(APIView):
    @classmethod
    def get(cls, request, file_id):
        if request.user.is_teacher:
            file = request.user.files.filter(id=file_id)
            if file.exists():
                serializer = FileSerializer(file[0])
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.user.is_student:
            file = request.user.accessed_files.filter(id=file_id)
            if file.exists():
                serializer = FileSerializer(file[0])
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

    @classmethod
    def put(cls, request, file_id):
        if request.user.is_teacher:
            if request.user.files.filter(id=file_id).exists():
                file = File.objects.get(id=file_id)
                serializer = FileSerializer(instance=file, data=request.data, context={"user": request.user})
                if serializer.is_valid():
                    serializer.save()
                    file = File.objects.get(id=serializer.data.get('id'))
                    file.students.set(User.objects.filter(id__in=request.data.get('students')))
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

    @classmethod
    def delete(cls, request, file_id):
        if request.user.is_teacher:
            file = request.user.files.filter(id=file_id)
            if file.exists():
                file[0].delete()
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_403_FORBIDDEN)
