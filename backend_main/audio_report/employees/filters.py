import django_filters
from .models import Employee
from departments.models import Department
from posts.models import Post


class EmployeeFilter(django_filters.FilterSet):
    department = django_filters.ModelMultipleChoiceFilter(queryset=Department.objects.all())
    post = django_filters.ModelMultipleChoiceFilter(queryset=Post.objects.all())

    class Meta:
        model = Employee
        fields = ['department', 'post']