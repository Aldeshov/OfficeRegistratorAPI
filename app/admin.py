from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Course, News, File, User

admin.site.register(User, UserAdmin)

admin.site.register(News)
admin.site.register(File)
admin.site.register(Course)
