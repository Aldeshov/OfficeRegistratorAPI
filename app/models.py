from django.contrib.auth.models import Permission
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models


class User(AbstractUser):
    type = models.PositiveSmallIntegerField(choices=((0, 'nobody'), (1, 'student'), (2, 'teacher'),), default=0)

    @property
    def is_student(self):
        return self.type == 1

    @property
    def is_teacher(self):
        return self.type == 2


class File(models.Model):
    name = models.CharField(max_length=64)
    path = models.CharField(max_length=256)
    owner = models.ForeignKey(User, related_name='files', on_delete=models.CASCADE)
    students = models.ManyToManyField(User, related_name='accessed_files', blank=True)


class Course(models.Model):
    name = models.CharField(max_length=64)
    room = models.CharField(max_length=64)
    schedule = ArrayField(ArrayField(models.IntegerField(), size=2))
    credits = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    teacher = models.ForeignKey(User, related_name='courses', on_delete=models.CASCADE)
    students = models.ManyToManyField(User, related_name='accessed_courses', blank=True)


class News(models.Model):
    title = models.CharField(max_length=128)
    date = models.DateField(auto_now_add=True)
    body = models.TextField()

    class Meta:
        verbose_name_plural = 'News'
