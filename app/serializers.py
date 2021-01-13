import datetime
from rest_framework import serializers
from django.contrib.auth.models import User
from app.models import Teacher, Course, Student, File, News


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class TeacherSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Teacher
        fields = ('id', 'user', 'user_id')


class CourseSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(write_only=True)
    user = UserSerializer(many=False, read_only=True)

    class Meta:
        model = Course
        fields = ('id', 'name', 'credits', 'schedule', 'room', 'user', 'user_id')


class FileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    path = serializers.CharField()
    owner = UserSerializer(read_only=True, many=False)
    owner_id = serializers.IntegerField(write_only=True)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name')
        instance.path = validated_data.get('path')
        instance.owner = User.objects.get(id=validated_data.get("owner_id"))
        instance.save()
        return instance

    def create(self, validated_data):
        return File.objects.create(**validated_data)


class StudentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    user = UserSerializer(many=False, read_only=True)
    courses = CourseSerializer(many=True, read_only=True)
    files = FileSerializer(many=True)

    class Meta:
        model = Student
        fields = ('id', 'user', 'courses', 'files')


class NewsSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField()
    body = serializers.CharField()
    date = serializers.DateField()

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title')
        instance.body = validated_data.get('body')
        instance.date = datetime.datetime.now()
        instance.save()
        return instance

    def create(self, validated_data):
        news = News.objects.create(title=validated_data.get('title'), body=validated_data.get('city'),
                                   date=datetime.datetime.now())
        return news
