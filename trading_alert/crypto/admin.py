from django.contrib import admin

from trading_alert.crypto.models import CriptoAlert


class CriptoAlertAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "current_price", "operator", "price", "currency")


admin.site.register(CriptoAlert, CriptoAlertAdmin)
