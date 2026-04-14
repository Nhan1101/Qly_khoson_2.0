from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("suppliers", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="chitietphieuxuat",
            name="don_gia",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
        migrations.AddField(
            model_name="phieuxuat",
            name="du_kien_giao",
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="phieuxuat",
            name="ly_do_xuat",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="phieuxuat",
            name="ma_don",
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name="phieuxuat",
            name="tong_tien",
            field=models.DecimalField(decimal_places=2, default=0, max_digits=15),
        ),
    ]
