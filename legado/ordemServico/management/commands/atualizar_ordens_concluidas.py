from django.core.management.base import BaseCommand

from legado.ordemServico.models import OrdemServico


class Command(BaseCommand):
    help = (
        "Atualiza o campo 'concluida' de todas as ordens de serviço conforme o "
        "status dos serviços relacionados."
    )

    def handle(self, *args, **options):
        total = OrdemServico.objects.count()
        concluidas = 0
        atualizadas = 0

        for ordem in OrdemServico.objects.prefetch_related("servicos"):
            concluida_antes = ordem.concluida
            if ordem.atualizar_status_conclusao():
                concluidas += 1
            if ordem.concluida != concluida_antes:
                atualizadas += 1

        msg = (
            f"{atualizadas} de {total} ordens tiveram o campo 'concluida' atualizado; "
            f"{concluidas} permanecem marcadas como concluídas."
        )
        self.stdout.write(self.style.SUCCESS(msg))


