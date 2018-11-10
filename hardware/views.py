from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView
from django_filters.views import FilterView
from django_tables2 import SingleTableMixin

from app.mixins import TabsViewMixin
from hardware.models import Request, HardwareType
from hardware.tables import RequestorTable, RequestorFilter, PickupTable, ReturnTable, RequestsTable, \
    AvailableHardwareTable, SelectCountHardwareTable, HackerRequests, HackerActive, HackerAvailableHardwareTable, \
    ActiveHardwareTable, HardwareTypeFilter, RequestFilter, HackerAvailableHardwareTableSelect
from user.mixins import IsHardwareAdminMixin
from user.models import User


@login_required
def root_view(request):
    user = request.user
    if user.is_organizer or user.is_hardware_admin or user.is_director:
        return HttpResponseRedirect(reverse('hw_pickupreturn'))
    else:
        return HttpResponseRedirect(reverse('hw_list'))


@cache_page(60)
def hardware_api(request):
    hws = HardwareType.prefetch_objects().all()
    ret = [{'name': hw.name, 'description': hw.description, 'total': hw.total_count, 'url': hw.url,
            'available': hw.available_count}
           for hw in hws]
    r = JsonResponse({'items': ret, 'update_time': timezone.now()})
    r._headers.update({'access': ('Access-Control-Allow-Origin', '*')})
    return r


def hardware_admin_tabs():
    return [
        ('Pick up/Return', reverse('hw_pickupreturn'), False),
        ('Available', reverse('hw_listall'), False),
        ('Active', reverse('hwad_active'), False),
    ]


def hardware_hacker_tabs(user):
    l = [
        ('Available', reverse('hw_list'), False),
    ]
    count = Request.pending_objects(user).count()
    if count:
        l.append(('Requested', reverse('hw_request'), count), )
    active = Request.active_objects(user).count()
    if active:
        l.append(('Active', reverse('hw_active'), active), )
    return l


# Admin views

class HardwarePickUpReturnView(TabsViewMixin, IsHardwareAdminMixin, SingleTableMixin, FilterView):
    template_name = 'hardware_requests.html'
    table_class = RequestorTable
    table_pagination = {'per_page': 50}
    filterset_class = RequestorFilter

    def get_current_tabs(self):
        return hardware_admin_tabs()

    def get_queryset(self):
        return User.objects.filter(is_volunteer=False, is_director=False, is_active=True, is_organizer=False)


class HackerPickupView(TabsViewMixin, IsHardwareAdminMixin, SingleTableMixin, TemplateView):
    template_name = 'hwadmin_pickup.html'
    table_class = PickupTable
    table_pagination = {'per_page': 50}

    def get_back_url(self):
        return reverse('hw_pickupreturn')

    def get_queryset(self):
        return Request.pending_objects(user_id=self.kwargs['id']).all()

    def get_context_data(self, **kwargs):
        c = super(HackerPickupView, self).get_context_data(**kwargs)
        c['user'] = User.objects.get(pk=self.kwargs['id'])
        return c

    def post(self, request, *args, **kwargs):
        selected = self.request.POST.getlist('selected')
        hws = Request.objects.filter(pk__in=selected)
        errors = {}
        for hw in hws:
            try:
                hw.pickup(request.user)
            except ValidationError as e:
                errors[hw.type.name] = ' '.join(e.messages)
        if errors.keys():
            messages.error(request,
                           'Failed to pick up: ' + ', '.join([str(k) + ':' + str(v) for k, v in errors.items()])
                           )
        return HttpResponseRedirect(reverse('hw_requestor', kwargs=self.kwargs))


class HackerReturnView(TabsViewMixin, IsHardwareAdminMixin, SingleTableMixin, TemplateView):
    template_name = 'hwadmin_return.html'
    table_class = ReturnTable
    table_pagination = {'per_page': 50}

    def get_back_url(self):
        return reverse('hw_pickupreturn')

    def get_context_data(self, **kwargs):
        c = super(HackerReturnView, self).get_context_data(**kwargs)
        c['user'] = User.objects.get(pk=self.kwargs['id'])
        return c

    def get_queryset(self):
        return Request.active_objects(user_id=self.kwargs['id']).all()

    def post(self, request, *args, **kwargs):
        selected = self.request.POST.getlist('selected')
        hws = Request.objects.filter(pk__in=selected)
        errors = {}
        for hw in hws:
            try:
                hw.return_(request.user)
            except ValidationError as e:
                errors[hw.type.name] = ' '.join(e.messages)
        if errors.keys():
            messages.error(request,
                           'Failed to return: ' + ', '.join([str(k) + ':' + str(v) for k, v in errors.items()]))
        return HttpResponseRedirect(reverse('hw_requestor', kwargs=self.kwargs))


class RequestsHistoricView(TabsViewMixin, IsHardwareAdminMixin, SingleTableMixin, TemplateView):
    template_name = 'hacker_historic_view.html'
    table_class = RequestsTable
    table_pagination = {'per_page': 50}

    def get_back_url(self):
        return reverse('hw_pickupreturn')

    def get_context_data(self, **kwargs):
        c = super(RequestsHistoricView, self).get_context_data(**kwargs)
        c['user'] = User.objects.get(pk=self.kwargs['id'])
        return c

    def get_queryset(self):
        return Request.historic_objects(self.kwargs['id']).all()


class HardwareAvailableAdmin(TabsViewMixin, IsHardwareAdminMixin, SingleTableMixin, FilterView):
    template_name = 'hardware_all.html'
    table_class = AvailableHardwareTable
    table_pagination = {'per_page': 50}
    filterset_class = HardwareTypeFilter

    def get_current_tabs(self):
        return hardware_admin_tabs()

    def get_queryset(self):
        return HardwareType.prefetch_objects().all()


class HardwareActiveAdmin(TabsViewMixin, IsHardwareAdminMixin, SingleTableMixin, FilterView):
    template_name = 'hwadmin_active.html'
    table_class = ActiveHardwareTable
    table_pagination = {'per_page': 50}
    filterset_class = RequestFilter

    def get_current_tabs(self):
        return hardware_admin_tabs()

    def get_queryset(self):
        return Request.active_overall().all()


# Hacker views

class HardwareAvailableView(TabsViewMixin, LoginRequiredMixin, SingleTableMixin, TemplateView):
    template_name = 'hardware_available.html'
    table_class = HackerAvailableHardwareTable
    table_pagination = {'per_page': 50}

    def get_table_class(self):
        if getattr(settings, 'HACKERS_CAN_REQUEST', True):
            return HackerAvailableHardwareTableSelect
        return HackerAvailableHardwareTable

    def get_current_tabs(self):
        return hardware_hacker_tabs(self.request.user)

    def get_context_data(self, **kwargs):
        c = super(HardwareAvailableView, self).get_context_data(**kwargs)
        c['form_action'] = reverse('hw_selectamount')
        c['form_method'] = 'get'
        return c

    def get_queryset(self):
        hws = HardwareType.prefetch_objects().all()
        return [h for h in hws if h.available_count > 0]


class HardwareSelectAmountView(TabsViewMixin, LoginRequiredMixin, SingleTableMixin, TemplateView):
    template_name = 'hardware_select.html'
    table_class = SelectCountHardwareTable
    table_pagination = {'per_page': 50}

    def get_back_url(self):
        return reverse('hw_list')

    def get_queryset(self):
        selected = self.request.GET.getlist('selected')
        hws = HardwareType.objects.filter(pk__in=selected)
        return [h for h in hws if h.available_count > 0]

    def post(self, request, *args, **kwargs):
        if not getattr(settings, 'HACKERS_CAN_REQUEST', True):
            messages.error(request, 'Hardware lab is not available at the moment!')
            return HttpResponseRedirect(reverse('hw_request'))

        ids = request.GET.getlist('selected')
        hws = HardwareType.objects.filter(pk__in=ids)
        errors = {}
        for hw in hws:
            amount = int(request.POST.get('amount_' + str(hw.pk), 0))
            for i in range(amount):
                if not hw.request(request.user):
                    errors[hw.type.name] = errors.get(hw.type.name, 0) + 1
        if errors.keys():
            messages.error(request, 'Couldn\'t request the following items:' + ', '.join(
                [str(k) + '(' + str(v) + ')' for k, v in errors.items()]
            ))

        return HttpResponseRedirect(reverse('hw_request'))


class HackerCurrentRequestView(TabsViewMixin, LoginRequiredMixin, SingleTableMixin, TemplateView):
    template_name = 'hacker_current_request.html'
    table_class = HackerRequests
    table_pagination = {'per_page': 50}

    def get_current_tabs(self):
        return hardware_hacker_tabs(self.request.user)

    def get_queryset(self):
        return Request.pending_objects(self.request.user.pk).all()


class HackerCurrentActiveView(TabsViewMixin, LoginRequiredMixin, SingleTableMixin, TemplateView):
    template_name = 'hacker_active.html'
    table_class = HackerActive
    table_pagination = {'per_page': 50}

    def get_current_tabs(self):
        return hardware_hacker_tabs(self.request.user)

    def get_queryset(self):
        return Request.active_objects(self.request.user.pk).all()
