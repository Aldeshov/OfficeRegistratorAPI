from django_filters import rest_framework as filters

from app.models import News, File


class NewsFilter(filters.FilterSet):
    title = filters.CharFilter(lookup_expr='contains')  # news = News.objects.filter(title__contains=title)

    class Meta:
        model = News
        fields = ('title', 'body', 'date')


class FileFilter(filters.FilterSet):
    path = filters.CharFilter(lookup_expr='startswith')
    teacher = filters.NumberFilter(field_name='owner_id')

    class Meta:
        model = File
        fields = ('path',)
