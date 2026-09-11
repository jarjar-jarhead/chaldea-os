import requests
from django.core.management.base import BaseCommand
from servants.models import Servant

class Command(BaseCommand):
    help = "Ingests Servant Spirit Origin records from Atlas Academy API into the database."

    def handle(self, *args, **options):
        url = "https://api.atlasacademy.io/export/NA/nice_servant.json"
        
        self.stdout.write(self.style.NOTICE("Initiating transmission with Atlas Academy API..."))
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            servants_data = response.json()
        except requests.exceptions.RequestException as error:
            self.stdout.write(self.style.ERROR(f"Transmission failed: {error}"))
            return

        self.stdout.write(f"Received {len(servants_data)} records. Processing Spirit Origins...")

        created_count = 0
        updated_count = 0

        # =======================================================
        # [TYPE YOUR CODE HERE: START OF CORE DATA PIPELINE]
        # =======================================================
        for item in servants_data:
            collection_no = item.get("collectionNo", 0)

            # we get them servants only, no npc and beast with no collection ID
            if collection_no <= 0:
                continue

            # get the radar stats of servants
            raw_params = item.get("profile", {}).get("stats", {}) or {}    

            defaults = {
                "name": item.get("name", "Unknown Spirit Origin"),
                "class_name": item.get("className", "Unknown").capitalize(),
                "rarity": item.get("rarity", 1),
                "cost": item.get("cost", 0),
                "atk_base": item.get("atkBase", 0),
                "atk_max": item.get("atkMax", 0),
                "hp_base": item.get("hpBase", 0),
                "hp_max": item.get("hpMax", 0),
                
                # Radar Parameters (Rank letters: A, B+, EX, etc.)
                "param_str": str(raw_params.get("strength", "E")),
                "param_end": str(raw_params.get("endurance", "E")),
                "param_agi": str(raw_params.get("agility", "E")),
                "param_mna": str(raw_params.get("magic", "E")),
                "param_lck": str(raw_params.get("luck", "E")),
                "param_np": str(raw_params.get("np", "E")),
                
                # Visual portrait from CDN
                "face_url": item.get("extraAssets", {}).get("faces", {}).get("1", None)

            }

            # Avoids duplicate row errors if run more than once
            obj, created = Servant.objects.update_or_create(
                collection_no = collection_no,
                defaults = defaults
            )

            if created:
                created_count += 1
            else:
                updated_count += 1
        # =======================================================
        # [END OF CORE DATA PIPELINE]
        # =======================================================

        self.stdout.write(
            self.style.SUCCESS(
                f"[SYSTEM OK] Sync complete! Created: {created_count} | Updated: {updated_count}"
            )
        )