from django.contrib import admin
from .models import Planet, Mission, Quiz, JigsawPuzzle


@admin.register(Planet)
class PlanetAdmin(admin.ModelAdmin):
    list_display = ("slug", "name", "is_unlocked")


class QuizInline(admin.TabularInline):
    model = Quiz
    extra = 0


class JigsawInline(admin.StackedInline):
    model = JigsawPuzzle
    extra = 0


@admin.register(Mission)
class MissionAdmin(admin.ModelAdmin):
    list_display = ("slug", "title", "planet", "mission_type", "is_cross_api",
                    "difficulty", "is_published", "created_at")
    list_filter = ("is_published", "mission_type", "planet", "is_cross_api")
    search_fields = ("slug", "title")
    filter_horizontal = ("prerequisites",)
    inlines = [QuizInline, JigsawInline]
