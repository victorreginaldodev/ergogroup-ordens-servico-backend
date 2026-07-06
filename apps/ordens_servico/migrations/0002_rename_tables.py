from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ordens_servico', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(name='ordemservico', table=None),
        migrations.AlterModelTable(name='servico', table=None),
        migrations.AlterModelTable(name='tarefa', table=None),
        migrations.AlterModelTable(name='ordemservicooperacional', table=None),
    ]
