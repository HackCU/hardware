from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from user.models import User


class HardwareType(models.Model):
    """Represents a kind of hardware"""

    # Human readable name
    name = models.CharField(max_length=50, unique=True)
    # Image of the hardware
    image = models.FileField(upload_to='hw_images/')
    # Description of this hardware
    # what is it used for? which items are contained in the package?
    description = models.CharField(max_length=200)

    # Number of items available for this type
    total_count = models.IntegerField(verbose_name='Items available')

    @classmethod
    def prefetch_objects(cls):
        return cls.objects.prefetch_related('requests')

    @property
    def not_available_count(self):
        time_expired = timezone.now() - timedelta(minutes=settings.HARDWARE_REQUEST_TIME)
        return self.requests.filter(Q(pickup_time__isnull=False, return_time__isnull=True) |
                                    Q(created_at__gte=time_expired, pickup_time__isnull=True)).count()

    @property
    def active_count(self):
        return self.requests.filter(pickup_time__isnull=False, return_time__isnull=True).count()

    @property
    def remaining_count(self):
        return self.total_count - self.active_count


    @property
    def available_count(self):
        return self.total_count - self.not_available_count

    def request(self, user):
        if self.available_count == 0:
            return None

        r = Request(requestor=user, type=self)
        r.save()
        return r


class Request(models.Model):
    """
    The 'item' has been borrowed to the 'user'
    """
    # User requesting hardware
    requestor = models.ForeignKey(User)

    # Type for this request
    type = models.ForeignKey(HardwareType, related_name='requests')

    # Instant of creation
    created_at = models.DateTimeField(auto_now_add=True)

    # If null: item has not been picked up yet
    pickup_time = models.DateTimeField(null=True, blank=True)

    # If null: item has not been returned yet
    return_time = models.DateTimeField(null=True, blank=True)

    # Organizer who gave out item
    borrowed_by = models.ForeignKey(User, null=True, blank=True, related_name='hardware_admin_borrowing')

    # Organizer who received back out item
    returned_to = models.ForeignKey(User, related_name='hardware_admin_return', null=True, blank=True)

    @classmethod
    def pending_objects(cls, user_id):
        time_expired = timezone.now() - timedelta(minutes=settings.HARDWARE_REQUEST_TIME)
        return cls.objects.filter(requestor_id=user_id, created_at__gte=time_expired, pickup_time__isnull=True)

    @classmethod
    def historic_objects(cls, user_id):
        time_expired = timezone.now() - timedelta(minutes=settings.HARDWARE_REQUEST_TIME)
        return cls.objects.filter(Q(requestor_id=user_id, created_at__gte=time_expired, pickup_time__isnull=True)
                                  | Q(requestor_id=user_id, pickup_time__isnull=False))

    @classmethod
    def active_objects(cls, user_id):
        return cls.objects.filter(requestor_id=user_id, pickup_time__isnull=False, return_time__isnull=True)

    @classmethod
    def active_overall(cls):
        return cls.objects.filter(pickup_time__isnull=False, return_time__isnull=True)

    @property
    def remaining_time(self):
        if self.pickup_time:
            return timedelta(seconds=0)
        return (self.created_at + timedelta(minutes=settings.HARDWARE_REQUEST_TIME)) - timezone.now()

    def pickup(self, organizer):
        if self.pickup_time:
            raise ValidationError('Request has been picked up already!')
        if self.remaining_time < timedelta(seconds=0):
            raise ValidationError('Request has expired!')
        if self.type.remaining_count <= 0:
            raise ValidationError('No items available')

        self.borrowed_by = organizer
        self.pickup_time = timezone.now()
        self.save()

    def return_(self, organizer):
        if not self.pickup_time and self.remaining_time > 0:
            raise ValidationError('Request has not been picked up yet')

        self.returned_to = organizer
        self.return_time = timezone.now()
        self.save()

    def cancel(self):
        if self.remaining_time < 0:
            raise ValidationError('Item has expired')
        if self.pickup_time:
            raise ValidationError('Item has been picked up')
        self.delete()
