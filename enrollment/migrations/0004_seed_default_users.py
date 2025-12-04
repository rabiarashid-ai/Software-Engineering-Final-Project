from django.db import migrations


def seed_users(apps, schema_editor):
    User = apps.get_model("auth", "User")
    users = [
        {
            "username": "stu",
            "email": "stu@example.com",
            "password": "st12345678",
            "is_staff": False,
            "is_superuser": False,
        },
        {
            "username": "adm",
            "email": "adm@example.com",
            "password": "ad12345678",
            "is_staff": True,
            "is_superuser": False,
        },
    ]
    for user in users:
        obj, _ = User.objects.get_or_create(
            username=user["username"],
            defaults={
                "email": user["email"],
                "is_staff": user["is_staff"],
                "is_superuser": user["is_superuser"],
            },
        )
        obj.is_staff = user["is_staff"]
        obj.is_superuser = user["is_superuser"]
        obj.set_password(user["password"])
        obj.save()


def unseed_users(apps, schema_editor):
    User = apps.get_model("auth", "User")
    User.objects.filter(username__in=["stu", "adm"]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("enrollment", "0003_seed_initial_courses"),
    ]

    operations = [
        migrations.RunPython(seed_users, unseed_users),
    ]
