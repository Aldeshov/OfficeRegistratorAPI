from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from app.models import Course, News, File, User
from app.filters import NewsFilter
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


@api_view(['GET', 'POST'])
def files_view(request, path, teacher):
    if request.method == 'GET':
        if request.user.is_student:
            files = request.user.accessed_files.filter(path__startswith=path)
            if teacher != 0:
                files = files.filter(owner_id=teacher)

            serializer = FileSerializer(files, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.user.is_teacher:
            files = request.user.files.filter(path__startswith=path)
            serializer = FileSerializer(files, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(status=status.HTTP_403_FORBIDDEN)

    elif request.method == 'POST':
        if request.user.is_teacher:
            student_ids = request.data.get('students')
            serializer = FileSerializer(data=request.data, context={"user": request.user})
            if serializer.is_valid():
                serializer.save()
                students = User.objects.filter(id__in=student_ids)
                File.objects.get(id=serializer.data.get('id')).students.set(students)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(status=status.HTTP_403_FORBIDDEN)


class CourseFile(APIView):
    @classmethod
    def get(cls, request, teacher, path, name):
        if request.user.is_teacher:
            file = request.user.files.filter(name=name, path=path)
            if file.exists():
                serializer = FileSerializer(file[0])
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.user.is_student:
            file = request.user.accessed_files.filter(owner_id=teacher, name=name, path=path)
            if file.exists():
                serializer = FileSerializer(file[0])
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

    @classmethod
    def put(cls, request, path, name, **kwargs):
        if request.user.is_teacher:
            file = request.user.files.filter(name=name, path=path)
            if file.exists():
                serializer = FileSerializer(
                    instance=File.objects.get(id=file[0].id),
                    data=request.data, context={"user": request.user}
                )
                if serializer.is_valid():
                    serializer.save()
                    students = User.objects.filter(id__in=request.data.get('students') or [])
                    File.objects.get(id=serializer.data.get('id')).students.set(students)
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_403_FORBIDDEN)

    @classmethod
    def delete(cls, request, path, name, **kwargs):
        if request.user.is_teacher:
            file = request.user.files.filter(name=name, path=path)
            if file.exists():
                file[0].delete()
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_403_FORBIDDEN)
