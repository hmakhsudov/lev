from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("real_estate", "0006_favorite"),
    ]

    operations = [
        migrations.AddField(
            model_name="propertyimage",
            name="image",
            field=models.FileField(blank=True, null=True, upload_to="property_images/"),
        ),
        migrations.AlterField(
            model_name="propertyimage",
            name="url",
            field=models.URLField(blank=True),
        ),
    ]
