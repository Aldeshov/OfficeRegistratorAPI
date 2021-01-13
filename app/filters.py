from django_filters import rest_framework as filters

from app.models import News


class NewsFilter(filters.FilterSet):
    # News.objects.filter(title__contains=title)
    title = filters.CharFilter(lookup_expr='contains')

    class Meta:
        model = News
        fields = ('title', 'body', 'date')
