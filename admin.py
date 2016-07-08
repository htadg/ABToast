from django.contrib import admin

from .models import Experiment, Test


class TestInline(admin.TabularInline):
    model = Test
    max_num = 2
    extra = 2


class ExperimentAdmin(admin.ModelAdmin):
    inlines = (TestInline, )
    list_display = ('name', 'start', 'end', 'is_active', )
    # exclude = ('status', )
    search_fields = ('name', )
    list_filter = ('start', 'end', 'is_active', )
    ordering = ('-start', )

admin.site.register(Experiment, ExperimentAdmin)
