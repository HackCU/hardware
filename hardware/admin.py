from django.contrib import admin
from django.utils.html import format_html

# Register your models here.
from hardware import models


class HardwareTypeAdmin(admin.ModelAdmin):
    def image_tag(self, obj):
        return format_html('<img src="{}" width="200"/>'.format(obj.image.url))

    image_tag.short_description = 'Image'

    list_display = ['name', 'image_tag']


class RequestAdmin(admin.ModelAdmin):

    list_display = ['requestor', 'type', 'created_at', 'pickup_time', 'return_time', 'remaining_time']


admin.site.register(models.HardwareType, HardwareTypeAdmin)
admin.site.register(models.Request, RequestAdmin)
