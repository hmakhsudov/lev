from rest_framework import serializers

from .models import Property, PropertyImage


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyImage
        fields = ["id", "url"]
        read_only_fields = ["id"]


class PropertySerializer(serializers.ModelSerializer):
    gallery = PropertyImageSerializer(many=True, read_only=True)
    price = serializers.DecimalField(
        max_digits=12, decimal_places=2, coerce_to_string=False
    )
    predicted_price = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        coerce_to_string=False,
        required=False,
        allow_null=True,
    )
    area_total = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        coerce_to_string=False,
        allow_null=True,
        required=False,
    )
    living_area = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        coerce_to_string=False,
        required=False,
        allow_null=True,
    )
    kitchen_area = serializers.DecimalField(
        max_digits=8,
        decimal_places=2,
        coerce_to_string=False,
        required=False,
        allow_null=True,
    )
    latitude = serializers.SerializerMethodField()
    longitude = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = [
            "id",
            "external_id",
            "source",
            "source_id",
            "title",
            "description",
            "price",
            "predicted_price",
            "area_total",
            "living_area",
            "kitchen_area",
            "rooms",
            "floor",
            "floors_total",
            "year_built",
            "property_type",
            "building_type",
            "address",
            "district",
            "city",
            "latitude",
            "longitude",
            "is_new_building",
            "images",
            "gallery",
            "main_image",
            "external_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "external_url",
            "source",
            "source_id",
            "main_image",
        ]

    def get_latitude(self, obj):
        return float(obj.latitude) if obj.latitude is not None else None

    def get_longitude(self, obj):
        return float(obj.longitude) if obj.longitude is not None else None

    def get_main_image(self, obj):
        images = obj.images or []
        if images:
            return images[0]
        first_photo = obj.gallery.first()
        return first_photo.url if first_photo else None


class PropertyWriteSerializer(serializers.ModelSerializer):
    gallery = PropertyImageSerializer(many=True, required=False)
    image_urls = serializers.ListField(
        child=serializers.URLField(), write_only=True, required=False, allow_empty=True
    )

    class Meta:
        model = Property
        fields = [
            "id",
            "external_id",
            "source",
            "source_id",
            "title",
            "description",
            "price",
            "predicted_price",
            "area_total",
            "living_area",
            "kitchen_area",
            "rooms",
            "floor",
            "floors_total",
            "year_built",
            "property_type",
            "building_type",
            "address",
            "district",
            "city",
            "latitude",
            "longitude",
            "is_new_building",
            "images",
            "image_urls",
            "gallery",
            "external_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        images_data = validated_data.pop("gallery", [])
        image_urls = validated_data.pop("image_urls", None)
        if image_urls is not None:
            validated_data["images"] = image_urls
            if not images_data:
                images_data = [{"url": url} for url in image_urls]
        property_obj = Property.objects.create(**validated_data)
        self._save_images(property_obj, images_data)
        return property_obj

    def update(self, instance, validated_data):
        images_data = validated_data.pop("gallery", None)
        image_urls = validated_data.pop("image_urls", None)
        if image_urls is not None:
            validated_data["images"] = image_urls
            if images_data is None:
                images_data = [{"url": url} for url in image_urls]
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if images_data is not None:
            instance.gallery.all().delete()
            self._save_images(instance, images_data)
        return instance

    def _save_images(self, property_obj, images_data):
        image_instances = [
            PropertyImage(property=property_obj, **image) for image in images_data
        ]
        PropertyImage.objects.bulk_create(image_instances)
