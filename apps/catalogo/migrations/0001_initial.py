import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Catalogo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=100)),
                ('descricao', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Catálogo',
                'verbose_name_plural': 'Catálogos',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='CatalogoOperacional',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=50)),
                ('descricao', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Catálogo Operacional',
                'verbose_name_plural': 'Catálogos Operacionais',
                'ordering': ['nome'],
            },
        ),
        migrations.CreateModel(
            name='SubitemCatalogo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=150)),
                ('descricao', models.TextField(blank=True, null=True)),
                ('ativo', models.BooleanField(default=True)),
                ('ordem', models.PositiveIntegerField(default=0)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('catalogo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subitens', to='catalogo.catalogo')),
            ],
            options={
                'verbose_name': 'Subitem de catálogo',
                'verbose_name_plural': 'Subitens de catálogo',
                'ordering': ['catalogo__nome', 'ordem', 'nome'],
            },
        ),
        migrations.AddConstraint(
            model_name='subitemcatalogo',
            constraint=models.UniqueConstraint(fields=('catalogo', 'nome'), name='unique_subitem_por_catalogo'),
        ),
    ]
