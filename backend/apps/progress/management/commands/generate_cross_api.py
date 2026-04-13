"""Generate cross-API missions. PLAN §2.3."""
from django.core.management.base import BaseCommand
from apps.games.services import generate_cross_api_missions


class Command(BaseCommand):
    help = "Generate cross-API missions from templates."

    def handle(self, *args, **options):
        missions = generate_cross_api_missions()
        for m in missions:
            self.stdout.write(f"  {m.slug}: {m.title}")
        self.stdout.write(self.style.SUCCESS(f"Done. {len(missions)} cross-API missions."))
