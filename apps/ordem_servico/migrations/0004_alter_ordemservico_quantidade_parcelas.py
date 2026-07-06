from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordem_servico', '0003_popular_status_liberacao_faturamento'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordemservico',
            name='quantidade_parcelas',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
