from django.contrib.auth.hashers import make_password
from django.db import migrations


def create_default_admin(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.update_or_create(
        email="admin@admin.admin",
        defaults={
            "password": make_password("Admin1234"),
            "role": "admin",
            "is_active": True,
            "is_staff": True,
            "is_superuser": True,
            "first_name": "Администратор",
            "last_name": "",
            "phone": "",
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_user_phone"),
    ]

    operations = [
        migrations.RunPython(create_default_admin, migrations.RunPython.noop),
    ]
