from rest_framework import serializers

from accounts.serializers import UserPublicSerializer
from .models import Property, PropertyImage


class PropertyImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = PropertyImage
        fields = ["id", "url", "image_url"]
        read_only_fields = ["id"]

    def get_image_url(self, obj):
        return _absolute_media_url(self.context.get("request"), obj)


class PropertySerializer(serializers.ModelSerializer):
    gallery = PropertyImageSerializer(many=True, read_only=True)
    images = serializers.SerializerMethodField()
    agent = UserPublicSerializer(source="created_by", read_only=True)
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
            "agent",
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
        images = self.get_images(obj)
        if images:
            return images[0]
        return None

    def get_images(self, obj):
        existing = list(obj.images or [])
        uploaded = [
            _absolute_media_url(self.context.get("request"), photo)
            for photo in obj.gallery.all()
        ]
        return list(dict.fromkeys(url for url in [*existing, *uploaded] if url))


class PropertyWriteSerializer(serializers.ModelSerializer):
    gallery = PropertyImageSerializer(many=True, required=False)
    image_urls = serializers.ListField(
        child=serializers.URLField(), write_only=True, required=False, allow_empty=True
    )
    image_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        allow_empty=True,
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
            "image_files",
            "gallery",
            "external_url",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_image_files(self, value):
        for image_file in value:
            content_type = getattr(image_file, "content_type", "")
            if content_type and not content_type.startswith("image/"):
                raise serializers.ValidationError("Загрузите файлы изображений.")
        return value

    def create(self, validated_data):
        images_data = validated_data.pop("gallery", [])
        image_urls = validated_data.pop("image_urls", None)
        image_files = validated_data.pop("image_files", None)
        if image_urls is not None:
            validated_data["images"] = image_urls
            if not images_data:
                images_data = [{"url": url} for url in image_urls]
        property_obj = Property.objects.create(**validated_data)
        self._save_images(property_obj, images_data)
        self._save_uploaded_images(property_obj, image_files)
        return property_obj

    def update(self, instance, validated_data):
        images_data = validated_data.pop("gallery", None)
        image_urls = validated_data.pop("image_urls", None)
        image_files = validated_data.pop("image_files", None)
        if image_urls is not None:
            validated_data["images"] = image_urls
            if images_data is None:
                images_data = [{"url": url} for url in image_urls]
        if image_files is not None:
            validated_data["images"] = []
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if images_data is not None or image_files is not None:
            instance.gallery.all().delete()
            self._save_images(instance, images_data)
            self._save_uploaded_images(instance, image_files)
        return instance

    def _save_images(self, property_obj, images_data):
        if not images_data:
            return
        image_instances = [
            PropertyImage(property=property_obj, **image) for image in images_data
        ]
        PropertyImage.objects.bulk_create(image_instances)

    def _save_uploaded_images(self, property_obj, image_files):
        if not image_files:
            return
        for image_file in image_files:
            PropertyImage.objects.create(property=property_obj, image=image_file)


def _absolute_media_url(request, photo):
    if not photo:
        return None
    if photo.url:
        return photo.url
    if not photo.image:
        return None
    url = photo.image.url
    return request.build_absolute_uri(url) if request else url
