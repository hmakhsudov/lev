from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("real_estate", "0004_property_source_id"),
    ]

    operations = [
        migrations.AlterField(
            model_name="property",
            name="floor",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="property",
            name="floors_total",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
