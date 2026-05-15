from django.db import models

from accounts.models import User


class Property(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ("apartment", "Apartment"),
        ("room", "Room"),
        ("house", "House"),
        ("commercial", "Commercial"),
    ]

    external_id = models.CharField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=64, blank=True, default="")
    source_id = models.CharField(max_length=32, blank=True, default="")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    area_total = models.DecimalField(
        max_digits=8, decimal_places=2, help_text="Square meters", null=True, blank=True
    )
    living_area = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    kitchen_area = models.DecimalField(
        max_digits=8, decimal_places=2, null=True, blank=True
    )
    rooms = models.PositiveIntegerField(null=True, blank=True)
    floor = models.PositiveIntegerField(null=True, blank=True)
    floors_total = models.PositiveIntegerField(null=True, blank=True)
    property_type = models.CharField(
        max_length=32, choices=PROPERTY_TYPE_CHOICES, default="apartment"
    )
    building_type = models.CharField(max_length=120, blank=True)
    address = models.CharField(max_length=255)
    district = models.CharField(max_length=120, blank=True)
    city = models.CharField(max_length=120, default="Санкт-Петербург")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    images = models.JSONField(default=list, blank=True)
    is_new_building = models.BooleanField(default=False)
    predicted_price = models.DecimalField(
        max_digits=12, decimal_places=2, null=True, blank=True
    )
    year_built = models.PositiveIntegerField(null=True, blank=True)
    external_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User, related_name="properties", null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"{self.title} - {self.price} ₽"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["external_id", "source"],
                condition=models.Q(external_id__isnull=False),
                name="unique_property_external_source",
            )
        ]


class PropertyImage(models.Model):
    property = models.ForeignKey(
        Property, related_name="gallery", on_delete=models.CASCADE
    )
    url = models.URLField(blank=True)
    image = models.FileField(upload_to="property_images/", blank=True, null=True)

    def __str__(self):
        return self.url or (self.image.url if self.image else "")


class Favorite(models.Model):
    user = models.ForeignKey(
        User, related_name="favorites", on_delete=models.CASCADE
    )
    property = models.ForeignKey(
        Property, related_name="favorited_by", on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "property"],
                name="unique_user_favorite_property",
            )
        ]

    def __str__(self):
        return f"{self.user_id} -> {self.property_id}"
