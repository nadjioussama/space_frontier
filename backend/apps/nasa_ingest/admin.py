from django.contrib import admin
from .models import APODEntry, EPICImage, Exoplanet, MarsPhoto, NEOApproach, NEOObject


@admin.register(APODEntry)
class APODEntryAdmin(admin.ModelAdmin):
    list_display = ("date", "title", "media_type", "is_published", "ingested_at")
    list_filter = ("is_published", "media_type")
    search_fields = ("title", "explanation")
    readonly_fields = ("ingested_at", "source_api", "source_id")


@admin.register(MarsPhoto)
class MarsPhotoAdmin(admin.ModelAdmin):
    list_display = ("rover", "camera", "sol", "earth_date", "is_published", "ingested_at")
    list_filter = ("rover", "camera", "is_published")
    search_fields = ("rover",)
    readonly_fields = ("ingested_at", "source_api", "source_id", "nasa_photo_id")


class NEOApproachInline(admin.TabularInline):
    model = NEOApproach
    extra = 0
    readonly_fields = ("approach_date", "velocity_kmh", "miss_distance_km",
                       "threat_score", "size_comparison")


@admin.register(NEOObject)
class NEOObjectAdmin(admin.ModelAdmin):
    list_display = ("name", "neo_id", "is_hazardous", "diameter_min_m", "diameter_max_m", "ingested_at")
    list_filter = ("is_hazardous",)
    search_fields = ("name", "neo_id")
    inlines = [NEOApproachInline]


@admin.register(EPICImage)
class EPICImageAdmin(admin.ModelAdmin):
    list_display = ("image_name", "date_taken", "centroid_lat", "centroid_lon", "is_published")
    list_filter = ("is_published",)
    readonly_fields = ("ingested_at", "source_api", "source_id", "identifier")


@admin.register(Exoplanet)
class ExoplanetAdmin(admin.ModelAdmin):
    list_display = ("name", "host_star", "habitability_score", "discovery_year", "is_published")
    list_filter = ("is_published",)
    search_fields = ("name", "host_star")
    readonly_fields = ("ingested_at", "source_api", "source_id")
