from rest_framework.permissions import BasePermission


class IsTeacherOrStudent(BasePermission):

    def has_permission(self, request, view):
        return bool(request.user.is_teacher or request.user.is_student)
