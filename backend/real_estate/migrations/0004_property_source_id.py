from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("real_estate", "0003_remove_property_area_property_area_total_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="property",
            name="source_id",
            field=models.CharField(blank=True, default="", max_length=32),
        ),
    ]
