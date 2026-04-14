from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("suppliers", "0002_export_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="phieuxuat",
            name="da_tao_don_giao_hang",
            field=models.BooleanField(default=False),
        ),
    ]
