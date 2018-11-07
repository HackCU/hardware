from django.contrib import admin

# Register your models here.
from hardware import models


class HardwareTypeAdmin(admin.ModelAdmin):

    list_display = ['name', 'description','total_count']


class RequestAdmin(admin.ModelAdmin):

    list_display = ['requestor', 'type', 'created_at', 'pickup_time', 'return_time', 'remaining_time']


admin.site.register(models.HardwareType, HardwareTypeAdmin)
admin.site.register(models.Request, RequestAdmin)
