import django.db.models.deletion
from django.db import migrations, models


def _renomear_content_types(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(app_label='servicos', model='repositorio').update(
        app_label='catalogo', model='catalogo',
    )
    ContentType.objects.filter(app_label='tarefas', model='repositoriominios').update(
        app_label='catalogo', model='catalogooperacional',
    )
    ContentType.objects.filter(app_label='servicos', model='subitemrepositorio').update(
        app_label='catalogo', model='subitemcatalogo',
    )


def _reverter_content_types(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    ContentType.objects.filter(app_label='catalogo', model='catalogo').update(
        app_label='servicos', model='repositorio',
    )
    ContentType.objects.filter(app_label='catalogo', model='catalogooperacional').update(
        app_label='tarefas', model='repositoriominios',
    )
    ContentType.objects.filter(app_label='catalogo', model='subitemcatalogo').update(
        app_label='servicos', model='subitemrepositorio',
    )


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('servicos', '0003_subitem_repositorio'),
        ('tarefas', '0001_initial'),
    ]

    operations = [
        # Adota as tabelas físicas existentes (servicos_repositorio, tarefas_repositoriominios)
        # sem recriá-las nem copiar dados — apenas move o estado do Django para o app catalogo.
        migrations.SeparateDatabaseAndState(
            state_operations=[
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
                        'db_table': 'servicos_repositorio',
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
                        'db_table': 'tarefas_repositoriominios',
                    },
                ),
            ],
            database_operations=[],
        ),
        # Idem para SubitemCatalogo, mas a FK muda de nome (repositorio -> catalogo),
        # então a coluna física precisa ser renomeada junto.
        migrations.SeparateDatabaseAndState(
            state_operations=[
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
                        'db_table': 'servicos_subitemrepositorio',
                    },
                ),
                migrations.AddConstraint(
                    model_name='subitemcatalogo',
                    constraint=models.UniqueConstraint(fields=('catalogo', 'nome'), name='unique_subitem_por_catalogo'),
                ),
            ],
            database_operations=[
                migrations.RunSQL(
                    sql=(
                        "ALTER TABLE servicos_subitemrepositorio "
                        "CHANGE COLUMN repositorio_id catalogo_id bigint NOT NULL, "
                        "RENAME INDEX unique_subitem_por_repositorio TO unique_subitem_por_catalogo"
                    ),
                    reverse_sql=(
                        "ALTER TABLE servicos_subitemrepositorio "
                        "CHANGE COLUMN catalogo_id repositorio_id bigint NOT NULL, "
                        "RENAME INDEX unique_subitem_por_catalogo TO unique_subitem_por_repositorio"
                    ),
                ),
            ],
        ),
        migrations.RunPython(_renomear_content_types, _reverter_content_types),
    ]
