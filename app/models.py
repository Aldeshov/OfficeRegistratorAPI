from django.contrib.auth.models import Permission
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.db import models


class File(models.Model):
    name = models.CharField(max_length=64)
    path = models.CharField(max_length=256)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)


class TeacherFileManager(models.Manager):
    def for_user(self, request):
        return File.objects.filter(owner=request.user)


class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    files = TeacherFileManager()
    objects = models.Manager()


class Course(models.Model):
    name = models.CharField(max_length=64)
    credits = models.IntegerField()
    schedule = ArrayField(ArrayField(models.IntegerField()))
    room = models.CharField(max_length=64)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    courses = models.ManyToManyField(Course)
    files = models.ManyToManyField(File, blank=True)


class News(models.Model):
    title = models.CharField(max_length=128)
    body = models.TextField()
    date = models.DateField()

    class Meta:
        verbose_name_plural = 'News'
