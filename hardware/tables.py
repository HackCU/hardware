import django_filters
import django_tables2 as tables
from django.db.models import Q

from hardware.models import Request, HardwareType
from user.models import User


class RequestorFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(email__icontains=value) | Q(name__icontains=value))

    class Meta:
        model = User
        fields = ['search']


class HardwareTypeFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(description__icontains=value))

    class Meta:
        model = HardwareType
        fields = ['search']


class RequestFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_filter', label='Search')

    def search_filter(self, queryset, name, value):
        return queryset.filter(Q(requestor__name__icontains=value) | Q(type__name__icontains=value))

    class Meta:
        model = Request
        fields = ['search']


class RequestorTable(tables.Table):
    return_ = tables.TemplateColumn(
        "<a href='{% url 'hw_return' record.id %}'>Return</a> ",
        verbose_name='Return', orderable=False)
    pickup = tables.TemplateColumn(
        "<a href='{% url 'hw_pickup' record.id %}'>Pick up</a> ",
        verbose_name='Pick up', orderable=False)
    history = tables.TemplateColumn(
        "<a href='{% url 'hw_requestor' record.id %}'>History</a> ",
        verbose_name='History', orderable=False)

    class Meta:
        model = User
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['name', 'return_', 'pickup', 'history']
        empty_text = 'No hackers matching'


class PickupTable(tables.Table):
    selected = tables.CheckBoxColumn(accessor="pk", verbose_name='Select')
    countdown = tables.TemplateColumn(
        template_name='include/countdown_column.html',
        verbose_name='Remaining time to pick up', orderable=False)

    class Meta:
        model = Request
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['selected', 'type.name', 'countdown']
        empty_text = 'No items have been requested. Ask hacker to fill request before!'


class ReturnTable(tables.Table):
    selected = tables.CheckBoxColumn(accessor="pk", verbose_name='Select')

    class Meta:
        model = Request
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['selected', 'type.name', 'pickup_time']
        empty_text = 'Hacker has returned all items!'


class RequestsTable(tables.Table):
    class Meta:
        model = Request
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['type.name', 'pickup_time', 'borrowed_by.email', 'return_time', 'returned_to.email']
        empty_text = 'No hardware request for current user'


class HackerRequests(tables.Table):
    countdown = tables.TemplateColumn(
        template_name='include/countdown_column.html',
        verbose_name='Remaining time to pick up', orderable=False)

    class Meta:
        model = Request
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['type.name', 'type.description', 'countdown']
        empty_text = 'No hardware requests for current user'


class HackerActive(tables.Table):
    class Meta:
        model = Request
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['type.name', 'type.description', 'pickup_time']
        empty_text = 'No hardware items currently in posession of user'


class AvailableHardwareTable(tables.Table):
    available = tables.TemplateColumn(
        "{{record.remaining_count}}/{{record.total_count}}",
        verbose_name='Remaining/Total', accessor="available_count", orderable=True)

    class Meta:
        model = HardwareType
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['name', 'description', 'available']
        empty_text = 'No hardware items at all'


class ActiveHardwareTable(tables.Table):
    class Meta:
        model = Request
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['type.name', 'requestor.name', 'pickup_time']
        empty_text = 'No hardware items active at all'


class HackerAvailableHardwareTable(tables.Table):
    selected = tables.CheckBoxColumn(accessor="pk", verbose_name='Select')
    available = tables.TemplateColumn(
        "{{record.available_count}}/{{record.total_count}}",
        verbose_name='Available/Total', accessor="available_count", orderable=True)

    class Meta:
        model = HardwareType
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['selected', 'name', 'description', 'available']
        empty_text = 'No hardware available. Check again to see when hackers requests expire'


class SelectCountHardwareTable(tables.Table):
    amount = tables.TemplateColumn(
        "<input type='number' min='0' max='{{record.available_count}}' name='amount_{{record.pk}}' value='1'/> ",
        verbose_name='Desired amount', orderable=False)

    class Meta:
        model = HardwareType
        attrs = {'class': 'table table-hover'}
        template = 'django_tables2/bootstrap-responsive.html'
        fields = ['name', 'description', 'available_count', ]
        empty_text = 'Items not available or no items selected. Go back to see current available items!'
