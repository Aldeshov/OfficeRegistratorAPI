from django.contrib import admin

from .models import Course, Student, Teacher, News, File

admin.site.register(Course)
admin.site.register(Student)
admin.site.register(Teacher)
admin.site.register(News)
admin.site.register(File)
