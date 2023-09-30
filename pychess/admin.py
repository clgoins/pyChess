from django.contrib import admin
from .models import *




@admin.action(description="Mark active")
def makeActive(modeladmin, request, queryset):
    queryset.update(isActive=True)

@admin.action(description="Mark inactive")
def makeInactive(modeladmin, request, queryset):
    queryset.update(isActive=False)


# Register your models here.
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    actions = [makeInactive, makeActive]

@admin.register(Move)
class MoveAdmin(admin.ModelAdmin):
    pass

