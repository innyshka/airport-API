from django.contrib import admin

from .models import (
    Airplane,
    Airport,
    AirplaneType,
    Crew,
    Route,
    Ticket,
    Flight,
    Order,
)

admin.site.register(Airplane)
admin.site.register(Airport)
admin.site.register(AirplaneType)
admin.site.register(Crew)
admin.site.register(Route)
admin.site.register(Ticket)
admin.site.register(Flight)
admin.site.register(Order)
