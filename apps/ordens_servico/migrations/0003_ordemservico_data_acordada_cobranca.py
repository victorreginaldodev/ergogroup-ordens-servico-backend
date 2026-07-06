from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordens_servico', '0002_rename_tables'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordemservico',
            name='data_acordada_cobranca',
            field=models.DateField(blank=True, null=True),
        ),
    ]
