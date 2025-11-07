from django.contrib import admin
from cats.models import SpyCat, Mission, Target


@admin.register(SpyCat)
class SpyCatAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'breed', 'years_of_experience', 'salary', 'created_at']
    list_filter = ['breed', 'created_at']
    search_fields = ['name', 'breed']
    readonly_fields = ['created_at', 'updated_at']


class TargetInline(admin.TabularInline):
    model = Target
    extra = 1
    fields = ['name', 'country', 'notes', 'complete']


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ['id', 'cat', 'complete', 'created_at']
    list_filter = ['complete', 'created_at']
    search_fields = ['cat__name']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [TargetInline]


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'country', 'mission', 'complete', 'created_at']
    list_filter = ['complete', 'country', 'created_at']
    search_fields = ['name', 'country']
    readonly_fields = ['created_at', 'updated_at']