import logging
import sys

from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django_apscheduler.jobstores import register_events

from render.models import ProtocoloAutorizacaoTeletrabalho

# Create scheduler to run in a thread inside the application process


def encaminhar_avaliacoes():
    print("Encaminhando avaliações!")
    avaliacoes_encaminhadas = []
    for protocolo_autorizacao in ProtocoloAutorizacaoTeletrabalho.objects.all():
        for avaliacao in protocolo_autorizacao.encaminha_pedido_avaliacao():
            avaliacoes_encaminhadas.append(avaliacao)

    n = len(avaliacoes_encaminhadas)
    print(f"-> [{n}] Avaliações encaminhadas")
    if n > 0:
        for avaliacao in avaliacoes_encaminhadas:
            print(avaliacao)


def start():
    if settings.DEBUG:
        # Hook into the apscheduler logger
        logging.basicConfig()
        logging.getLogger("apscheduler").setLevel(logging.DEBUG)

    scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)

    scheduler.add_job(
        encaminhar_avaliacoes,
        trigger="cron",
        year="*",
        month="*",
        day="last",
        name="encaminhar_avaliacoes",
        jobstore="default",
    )

    # Add the scheduled jobs to the Django admin interface
    register_events(scheduler)

    scheduler.start()
    print("Scheduler started ...", file=sys.stdout)
