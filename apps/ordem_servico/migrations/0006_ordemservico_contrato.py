from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ordem_servico', '0005_ordemservico_faturada_por'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordemservico',
            name='contrato',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='objeto_contrato',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='contrato_data_inicio',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='contrato_data_fim',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='gestor_contrato_nome',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='gestor_contrato_email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='gestor_contrato_telefone',
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
