from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Log

@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'accion', 'descripcion', 'fecha')
    list_filter = ('accion', 'fecha')
    search_fields = ('usuario__username', 'descripcion')
    ordering = ('-fecha',)
