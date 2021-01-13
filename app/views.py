from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from app.serializers import CourseSerializer, StudentSerializer,  UserSerializer, NewsSerializer, FileSerializer
from .models import Course, Student, Teacher, News, File
from django.contrib.auth.forms import PasswordChangeForm
from django_filters.rest_framework import DjangoFilterBackend
from app.filters import NewsFilter


def this_user(request):
    if request.user.is_authenticated:
        try:
            return Student.objects.get(user=request.user)
        except Student.DoesNotExist as next_s:
            try:
                return Teacher.objects.get(user=request.user)
            except Teacher.DoesNotExist as next_t:
                print("-  " + str(next_s))
                print("-  " + str(next_t))
                return None
    else:
        return None


class CourseListAPIView(APIView):
    def get(self, request):
        user = this_user(request)
        if user.__class__.__name__ == Student.__name__:
            courses = [c for c in Course.objects.all() if c in user.courses.all()]
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data)
        elif user.__class__.__name__ == Teacher.__name__:
            courses = [c for c in Course.objects.all() if c.teacher == user]
            serializer = CourseSerializer(courses, many=True)
            return Response(serializer.data)

    def post(self, request):
        user = this_user(request)
        if user.__class__.__name__ == Teacher.__name__:
            serializer = CourseSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors)
        return Response({'error': "Not Access"},
                        status=status.HTTP_406_NOT_ACCEPTABLE)


class StudentListAPIView(APIView):
    def get(self, request):
        user = this_user(request)
        if user.__class__.__name__ == Teacher.__name__:
            students = Student.objects.all()
            serializer = StudentSerializer(students, many=True)
            return Response(serializer.data)


class NewsListAPIView(generics.ListCreateAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    filter_backends = (DjangoFilterBackend,)
    filter_class = NewsFilter


class CurrentUser(APIView):
    def get(self, request):
        if request.user.is_anonymous:
            return Response({'error': "Not Access"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            serializer = UserSerializer(request.user, many=False)
            data = serializer.data
            if this_user(request).__class__.__name__ == Teacher.__name__:
                data.update({"type": "Teacher"})
            elif this_user(request).__class__.__name__ == Student.__name__:
                data.update({"type": "Student"})
            return Response(data)

    def put(self, request):
        if request.user.is_anonymous:
            return Response({'error': "Not Access"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            data = {
                "old_password": request.data.get("old_password"),
                "new_password1": request.data.get("new_password1"),
                "new_password2": request.data.get("new_password2"),
            }

            form = PasswordChangeForm(request.user, data)

            if form.is_valid():
                data = {
                    "id": request.user.id,
                    "username": request.data.get("username"),
                    "first_name": request.data.get("first_name"),
                    "last_name": request.data.get("last_name"),
                    "email": request.data.get("email")
                }
                serializer = UserSerializer(instance=User.objects.get(id=request.user.id),
                                            data=data, many=False)
                if serializer.is_valid():
                    serializer.save()
                    user = form.save()
                    update_session_auth_hash(request, user)  # Important!
                    return Response(serializer.data)
                return Response({"ERROR": serializer.errors})
            else:
                return Response({"ERROR": form.errors})


class CourseDetailAPIView(APIView):
    def get(self, request, course_id):
        user = this_user(request)
        if user:
            try:
                course = Course.objects.get(id=course_id)
            except Course.DoesNotExist as e:
                return Response({'error': str(e)})
            serializer = CourseSerializer(course)
            return Response(serializer.data)
        else:
            return Response({'error': 'Not Access'}, status=status.HTTP_401_UNAUTHORIZED)


class UserAPIView(APIView):
    def get(self, request, user_id):
        if request.user.is_anonymous:
            return Response({'error': 'Not Access'}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            try:
                user = User.objects.get(id=user_id)
            except Course.DoesNotExist as e:
                return Response({'error': str(e)})
            serializer = UserSerializer(user)
            return Response(serializer.data)


@api_view(['GET', 'POST'])
def files_view(request, path, teacher):
    if request.method == 'GET':
        user = this_user(request)
        if user.__class__.__name__ == Student.__name__:
            files = []
            for f in File.objects.all():
                if f in user.files.all() and f.path.startswith(path):
                    if teacher != 0 and f.owner.id == teacher:
                        files.append(f)
                    elif teacher == 0:
                        files.append(f)
            if len(files) == 0:
                return Response({"NULL": "WRONG PATH"})
            serializer = FileSerializer(files, many=True)
            data = serializer.data
            for el in data:
                el.update({"access": "Student"})
            return Response(data)
        elif user.__class__.__name__ == Teacher.__name__:
            files = []
            for f in Teacher.files.for_user(request):
                if f.path.startswith(path):
                    files.append(f)
            if len(files) == 0:
                return Response({"NULL": "WRONG PATH"})
            serializer = FileSerializer(files, many=True)
            data = serializer.data
            for el in data:
                el.update({"access": "Teacher"})
            return Response(data)

    elif request.method == 'POST':
        user = this_user(request)
        if user.__class__.__name__ == Teacher.__name__:
            students = request.data.get('students')
            new_file = {
                'name': request.data.get('name'),
                'path': request.data.get('path'),
                'owner_id': request.data.get('owner_id')
            }
            serializer = FileSerializer(data=new_file)
            if serializer.is_valid():
                serializer.save()
                for s in students:
                    s = Student.objects.get(id=s)
                    s.files.add(File.objects.get(name=request.data.get('name'), path=request.data.get('path')))
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            print(serializer.errors)
            return Response({'error': serializer.errors},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({'error': "Not Access"}, status=status.HTTP_406_NOT_ACCEPTABLE)


class CourseFile(APIView):
    def get_file(self, request, teacher, path, name):
        try:
            if request.method == "PUT" or request.method == "DELETE":
                if this_user(request).__class__.__name__ == Teacher.__name__:
                    return Teacher.files.for_user(request).get(owner=User.objects.get(id=teacher), name=name, path=path)
                else:
                    return None
            if this_user(request).__class__.__name__ == Student.__name__ :
                return this_user(request).files.all().get(owner_id=teacher, name=str(name), path=str(path))
            else:
                return File.objects.get(owner=User.objects.get(id=teacher), name=name, path=path)
        except Exception as error:
            print(error)
            return None

    def get(self, request, teacher, path, name):
        if not this_user(request):
            return Response({'error': "Not Access"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            if self.get_file(request, teacher, path, name):
                file = self.get_file(request, teacher, path, name)
            else:
                return Response({"error": "Not Found"})
            serializer = FileSerializer(file, many=False)
            data = serializer.data
            if this_user(request).__class__.__name__ == Teacher.__name__:
                data.update({"access": "Teacher"})
            elif this_user(request).__class__.__name__ == Student.__name__:
                data.update({"access": "Student"})
            return Response(data)

    def put(self, request, teacher, path, name):
        if request.user.is_anonymous:
            return Response({'error': "Not Access"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            if self.get_file(request, teacher, path, name):
                file = self.get_file(request, teacher, path, name)
            else:
                return Response({"error": "Not Found"})
            data = request.data
            data["owner_id"] = file.owner.id
            if not data.get("name"):
                data["name"] = file.name
            if not data.get("path"):
                data["path"] = file.path

            serializer = FileSerializer(instance=file, data=data)
            if serializer.is_valid():
                serializer.save()
                students = request.data.get('students')
                for s in students:
                    s = Student.objects.get(id=s)
                    if not s.files.check(name=request.data.get('name'), path=request.data.get('path')):
                        s.files.add(File.objects.get(name=request.data.get('name'), path=request.data.get('path')))
                return Response(serializer.data, status=status.HTTP_200_OK)
            print(serializer.errors)
            return Response({'error': serializer.errors}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request, teacher, path, name):
        if request.user.is_anonymous:
            return Response({'error': "Not Access"}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            if self.get_file(request, teacher, path, name):
                file = self.get_file(request, teacher, path, name)
            else:
                return Response({"error": "Not Found"})
            file.delete()
            return Response({"deleted": True}, status=status.HTTP_200_OK)
