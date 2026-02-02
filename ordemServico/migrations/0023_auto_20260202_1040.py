from django.db import migrations

def marcar_revisao_cliente(apps, schema_editor):
    # Usamos o apps.get_model para evitar problemas com imports circulares
    MiniOS = apps.get_model('ordemServico', 'MiniOS')
    
    # Filtra MiniOS onde o nome do repositório (servico) contém a string de correção
    minios_com_correcao = MiniOS.objects.filter(
        servico__nome__icontains="Correção Cliente"
    )
    
    # Atualiza todos de uma vez para ganhar performance
    minios_com_correcao.update(revisao_cliente=True)

class Migration(migrations.Migration):

    dependencies = [
        ('ordemServico', '0022_minios_revisao_cliente'),
    ]

    operations = [
        migrations.RunPython(marcar_revisao_cliente),
    ]
