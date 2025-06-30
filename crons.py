# cataliticos/crons.py
from django_cron import CronJobBase, Schedule
from django.core.management import call_command

class CargarPreciosCron(CronJobBase):
    RUN_EVERY_MINS = 1440  # cada 24 horas

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = 'cataliticos.cargar_precios_cron'  # nombre único

    def do(self):
        call_command('cargar_precios_goldapi')
