from django.apps import AppConfig


class AppNameConfig(AppConfig):
    name = "scheduler"

    def ready(self):
        from scheduler import scheduler

        scheduler.start()
