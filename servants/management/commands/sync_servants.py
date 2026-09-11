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
            if collection_no <= 0:
                continue

            raw_params = item.get("profile", {}).get("stats", {}) or {}

            # 1. Deck Parser (Converts ['quick', 'arts', 'arts', 'buster', 'buster'] -> 'QAABB')
            cards_list = item.get("cards", [])
            deck_code = "".join([c[0].upper() for c in cards_list if c]) or "QAABB"

            # 2. Noble Phantasm Parser (Extracts the primary active NP)
            noble_phantasms = item.get("noblePhantasms", [])
            active_np = noble_phantasms[0] if noble_phantasms else {}
            np_name = active_np.get("name", "Unknown Phantasm")
            np_card = active_np.get("card", "Buster").capitalize()
            np_type = active_np.get("effectFlags", [])
            # Fallback for NP targeting display
            np_type_label = active_np.get("target", "Support")
            if "aoe" in str(active_np).lower():
                np_type_label = "Anti-Army (AoE)"
            elif "single" in str(active_np).lower():
                np_type_label = "Anti-Unit (ST)"

            # 3. Hidden Attribute & Alignment
            attribute = item.get("attribute", "Earth").capitalize()
            raw_traits = item.get("traits", [])
            # In Atlas Academy, alignment is often in profile or traits; fallback clean string
            alignment = f"{attribute} Attribute"

            # 4. Ascension Art Stages (charaGraph CDN images)
            graphs = item.get("extraAssets", {}).get("charaGraph", {}).get("ascension", {}) or {}
            stage1 = graphs.get("1") or item.get("extraAssets", {}).get("faces", {}).get("1")
            stage2 = graphs.get("2") or stage1
            stage3 = graphs.get("3") or stage2
            stage4 = graphs.get("4") or stage3

            defaults = {
                "name": item.get("name", "Unknown Spirit Origin"),
                "class_name": item.get("className", "Unknown").capitalize(),
                "rarity": item.get("rarity", 1),
                "cost": item.get("cost", 0),
                "atk_base": item.get("atkBase", 0),
                "atk_max": item.get("atkMax", 0),
                "hp_base": item.get("hpBase", 0),
                "hp_max": item.get("hpMax", 0),
                
                # New Attributes
                "attribute": attribute,
                "alignment": alignment,
                "deck": deck_code,
                "np_name": np_name,
                "np_card": np_card,
                "np_type": np_type_label,

                # Parameters
                "param_str": str(raw_params.get("strength", "E")),
                "param_end": str(raw_params.get("endurance", "E")),
                "param_agi": str(raw_params.get("agility", "E")),
                "param_mna": str(raw_params.get("magic", "E")),
                "param_lck": str(raw_params.get("luck", "E")),
                "param_np": str(raw_params.get("np", "E")),
                
                # Visuals
                "face_url": item.get("extraAssets", {}).get("faces", {}).get("1", None),
                "art_stage1": stage1,
                "art_stage2": stage2,
                "art_stage3": stage3,
                "art_stage4": stage4,
            }

            obj, created = Servant.objects.update_or_create(
                collection_no=collection_no,
                defaults=defaults
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