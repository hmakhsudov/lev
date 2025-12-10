from django.contrib import admin

from .models import Property, PropertyImage


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    inlines = [PropertyImageInline]
    list_display = (
        "title",
        "price",
        "area_total",
        "rooms",
        "district",
        "property_type",
        "is_new_building",
        "source",
        "source_id",
        "external_id",
        "created_at",
    )
    list_filter = ("district", "property_type", "source")
    search_fields = ("title", "address", "district", "city", "external_id", "source_id")


@admin.register(PropertyImage)
class PropertyImageAdmin(admin.ModelAdmin):
    list_display = ("property", "url")
