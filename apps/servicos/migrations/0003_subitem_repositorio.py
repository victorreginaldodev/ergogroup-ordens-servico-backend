from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('servicos', '0002_rastreio_status_servico'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubitemRepositorio',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=150)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('ativo', models.BooleanField(default=True)),
                ('ordem', models.PositiveIntegerField(default=0)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('repositorio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subitens', to='servicos.repositorio')),
            ],
            options={
                'verbose_name': 'Subitem de repositorio',
                'verbose_name_plural': 'Subitens de repositorio',
                'ordering': ['repositorio__nome', 'ordem', 'nome'],
            },
        ),
        migrations.AddConstraint(
            model_name='subitemrepositorio',
            constraint=models.UniqueConstraint(fields=('repositorio', 'nome'), name='unique_subitem_por_repositorio'),
        ),
    ]
