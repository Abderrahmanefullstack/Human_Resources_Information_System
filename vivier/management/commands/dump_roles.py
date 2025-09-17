from django.core.management.base import BaseCommand
from collections import Counter
from django.utils import timezone
from agents.models import Agent


def _ok_3ans(d):
    if not d:
        return False
    try:
        d0 = d if hasattr(d, "year") else d.date()
    except Exception:
        return False
    return (timezone.localdate() - d0).days >= 365 * 3


class Command(BaseCommand):
    help = "Dump des libellés de fonction (fréquences), avec et sans filtre ≥ 3 ans."

    def add_arguments(self, parser):
        parser.add_argument(
            "--top", type=int, default=50, help="Nombre de lignes à afficher"
        )

    def handle(self, *args, **opts):
        top = opts["top"]

        labels_all = Counter()
        labels_3y = Counter()

        for ag in Agent.objects.using("default").all():
            lbl = (ag.FonctionLibelle or "").strip()
            if not lbl:
                continue
            labels_all[lbl] += 1
            if _ok_3ans(getattr(ag, "DateEffetFonction", None)):
                labels_3y[lbl] += 1

        self.stdout.write("\n== Top libellés (TOUS) ==")
        for lab, cnt in labels_all.most_common(top):
            self.stdout.write(f"{cnt:>5}  {lab}")

        self.stdout.write("\n== Top libellés (≥3 ans) ==")
        for lab, cnt in labels_3y.most_common(top):
            self.stdout.write(f"{cnt:>5}  {lab}")
