from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("suppliers", "0002_sample_accounts"),
    ]

    operations = [
        migrations.AlterField(
            model_name="nguoidung",
            name="vai_tro",
            field=models.CharField(
                choices=[("Admin", "Admin"), ("NhanVien", "NhanVien")],
                max_length=50,
            ),
        ),
    ]

