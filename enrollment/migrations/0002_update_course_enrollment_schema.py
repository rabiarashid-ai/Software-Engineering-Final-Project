from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("enrollment", "0001_initial"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="enrollment",
            name="unique_user_course_enrollment",
        ),
        migrations.RenameField(
            model_name="enrollment",
            old_name="user",
            new_name="student",
        ),
        migrations.AddField(
            model_name="course",
            name="code",
            field=models.CharField(default="", max_length=20),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="course",
            name="credits",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="course",
            name="semester",
            field=models.CharField(default="", max_length=50),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name="course",
            name="end_date",
        ),
        migrations.RemoveField(
            model_name="course",
            name="instructor",
        ),
        migrations.RemoveField(
            model_name="course",
            name="start_date",
        ),
        migrations.AlterModelOptions(
            name="course",
            options={"ordering": ["code"]},
        ),
        migrations.AddConstraint(
            model_name="enrollment",
            constraint=models.UniqueConstraint(
                fields=("student", "course"), name="unique_student_course_enrollment"
            ),
        ),
    ]
