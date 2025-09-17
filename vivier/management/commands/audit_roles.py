from django.core.management.base import BaseCommand
from collections import Counter
from vivier.utils import _parse_role, _ok_3ans
from agents.models import Agent


class Command(BaseCommand):
    help = (
        "Audit des libellés fonction (≥3 ans) : famille/niveau détectés par le parseur."
    )

    def handle(self, *args, **options):
        rows = []
        total = 0

        qs = Agent.objects.using("default").all()
        for ag in qs:
            total += 1
            d = getattr(ag, "DateEffetFonction", None)
            if not _ok_3ans(d):
                continue
            label = getattr(ag, "FonctionLibelle", "") or ""
            fam, lvl = _parse_role(label)
            rows.append((label, fam, lvl))

        self.stdout.write(f"Total agents en base : {total}")
        self.stdout.write(f"≥ 3 ans dans la fonction : {len(rows)}\n")

        fam_counter = Counter(f for _, f, _ in rows)
        self.stdout.write("Top familles détectées (≥3 ans) :")
        for fam, cnt in fam_counter.most_common(20):
            self.stdout.write(f" - {fam or '??'} : {cnt}")

        self.stdout.write("\nExemples non détectés (famille vide) :")
        shown = 0
        for lab, fam, lvl in rows:
            if not fam:
                self.stdout.write(f"  * {lab}")
                shown += 1
            if shown >= 20:
                break
