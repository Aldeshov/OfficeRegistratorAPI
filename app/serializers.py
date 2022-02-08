from rest_framework import serializers
from app.models import Course, File, News, User


class NewsSerializer(serializers.ModelSerializer):
    date = serializers.DateField(read_only=True)

    class Meta:
        model = News
        fields = ('title', 'date', 'body')


class UserSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    is_student = serializers.ReadOnlyField()
    is_teacher = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'is_student', 'is_teacher', 'username', 'first_name', 'last_name', 'email')


class CourseSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField()
    room = serializers.CharField()
    credits = serializers.IntegerField()
    teacher = UserSerializer(read_only=True)
    schedule = serializers.ListField(child=serializers.ListField(child=serializers.IntegerField()))

    def validate(self, data):
        if not self.context.get('user') or not self.context.get('user').is_teacher:
            raise serializers.ValidationError("Current user must be teacher")
        return data

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name')
        instance.room = validated_data.get('room')
        instance.credits = validated_data.get('credits')
        instance.save()
        return instance

    def create(self, validated_data):
        validated_data.setdefault('teacher', self.context.get('user'))
        return Course.objects.create(**validated_data)


class FileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    owner = UserSerializer(read_only=True)
    name = serializers.CharField()
    path = serializers.CharField()

    def validate(self, data):
        if not self.context.get('user') or not self.context.get('user').is_teacher:
            raise serializers.ValidationError("Current user must be teacher")
        return data

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name') or instance.name
        instance.path = validated_data.get('path') or instance.path
        instance.save()
        return instance

    def create(self, validated_data):
        validated_data.setdefault('owner', self.context.get('user'))
        return File.objects.create(**validated_data)
