from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalogo', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelTable(name='catalogo', table=None),
        migrations.AlterModelTable(name='catalogooperacional', table=None),
        migrations.AlterModelTable(name='subitemcatalogo', table=None),
    ]
