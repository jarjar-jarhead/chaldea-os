import requests
from django.core.management.base import BaseCommand
from servants.models import Servant

class Command(BaseCommand):
    help = "Ingests Servant records, including skills, passives, and NP details from Atlas Academy."

    def handle(self, *args, **options):
        url = "https://api.atlasacademy.io/export/NA/nice_servant.json"
        
        self.stdout.write(self.style.NOTICE("Connecting to Atlas Academy API..."))
        
        try:
            response = requests.get(url, timeout=60)
            response.raise_for_status()
            servants_data = response.json()
        except requests.exceptions.RequestException as error:
            self.stdout.write(self.style.ERROR(f"Transmission failed: {error}"))
            return

        self.stdout.write(f"Received {len(servants_data)} records. Ingesting skills and lore...")

        card_map = {
            1: "A", "1": "A", "arts": "A",
            2: "B", "2": "B", "buster": "B",
            3: "Q", "3": "Q", "quick": "Q",
        }

        updated_count = 0
        created_count = 0

        for item in servants_data:
            collection_no = item.get("collectionNo", 0)
            if not collection_no or collection_no <= 0:
                continue

            # 1. Command Deck Mapping
            raw_cards = item.get("cards", [])
            deck = "".join([card_map.get(c, "B") for c in raw_cards]) or "QAABB"

            # 2. Noble Phantasm Extraction
            nps = item.get("noblePhantasms", [])
            active_np = nps[0] if nps else {}
            np_name = active_np.get("name", "Unknown Noble Phantasm")
            np_detail = active_np.get("detail", "Deals substantial damage to targets.")
            
            raw_np_card = active_np.get("card", "Buster")
            np_card = card_map.get(raw_np_card, str(raw_np_card).capitalize())
            if np_card == "A": np_card = "Arts"
            elif np_card == "B": np_card = "Buster"
            elif np_card == "Q": np_card = "Quick"

            raw_target = str(active_np.get("target", "Support")).lower()
            if "aoe" in raw_target or "all" in raw_target:
                np_type = "Anti-Army (AoE)"
            elif "pt" in raw_target or "single" in raw_target or "one" in raw_target:
                np_type = "Anti-Unit (ST)"
            else:
                np_type = "Support"

            # 3. Active Skills (Primary 3 skills)
            raw_skills = item.get("skills", [])
            active_skills = []
            for s in raw_skills[:3]:
                active_skills.append({
                    "num": s.get("num", 1),
                    "name": s.get("name", "Unknown Skill"),
                    "detail": s.get("detail", "No tactical telemetry recorded."),
                    "icon": s.get("icon", ""),
                })

            # 4. Passive Skills
            raw_passives = item.get("classPassive", [])
            passive_skills = []
            for p in raw_passives:
                passive_skills.append({
                    "name": p.get("name", "Class Passive"),
                    "detail": p.get("detail", ""),
                    "icon": p.get("icon", ""),
                })

            # 5. Lore / Profile snippets (From traits and battle comments)
            traits = [t.get("name") for t in item.get("traits", []) if t.get("name")]
            profile_lore = [
                f"Registered Class: {item.get('className', 'Unknown').capitalize()}",
                f"Tactical Alignment: {item.get('attribute', 'Earth').capitalize()} Attribute",
                f"Spirit Traits: {', '.join(traits[:8]) if traits else 'Humanoid'}"
            ]

            # 6. Images
            extra_assets = item.get("extraAssets") or {}
            faces_asc = (extra_assets.get("faces") or {}).get("ascension") or {}
            chara_asc = (extra_assets.get("charaGraph") or {}).get("ascension") or {}

            face_url = faces_asc.get("1") or faces_asc.get(1) or faces_asc.get("0") or None
            art1 = chara_asc.get("1") or chara_asc.get(1) or face_url
            art2 = chara_asc.get("2") or chara_asc.get(2) or art1
            art3 = chara_asc.get("3") or chara_asc.get(3) or art2
            art4 = chara_asc.get("4") or chara_asc.get(4) or art3

            # 7. Parameters
            atk = item.get("atkMax", 10000)
            hp = item.get("hpMax", 12000)
            star_gen = item.get("starGen", 100) / 10
            star_absorb = item.get("starAbsorb", 100)
            rarity = item.get("rarity", 3)

            str_rank = "EX" if atk > 12000 else "A" if atk > 10500 else "B" if atk > 9000 else "C" if atk > 7500 else "D"
            end_rank = "EX" if hp > 15000 else "A" if hp > 13500 else "B" if hp > 11500 else "C" if hp > 9500 else "D"
            agi_rank = "A" if star_gen > 11 else "B" if star_gen > 9 else "C" if star_gen > 7 else "D"
            mna_rank = "EX" if deck.count("A") >= 3 else "A" if deck.count("A") == 2 else "B" if rarity >= 4 else "C"
            lck_rank = "A+" if star_absorb > 150 else "B" if star_absorb > 90 else "C" if star_absorb > 40 else "D"
            np_rank = "EX" if rarity == 5 else "A" if rarity == 4 else "B" if rarity == 3 else "C"

            atlas_id = item.get("id", 0)

            defaults = {
                "atlas_id": atlas_id,
                "name": item.get("name", "Unknown Spirit Origin"),
                "class_name": item.get("className", "Unknown").capitalize(),
                "rarity": rarity,
                "cost": item.get("cost", 0),
                "atk_base": item.get("atkBase", 0),
                "atk_max": atk,
                "hp_base": item.get("hpBase", 0),
                "hp_max": hp,
                "attribute": str(item.get("attribute", "Earth")).capitalize(),
                "alignment": f"{str(item.get('attribute', 'Earth')).capitalize()} Attribute",
                "deck": deck,
                "np_name": np_name,
                "np_card": np_card,
                "np_type": np_type,
                "np_detail": np_detail,
                "active_skills": active_skills,
                "passive_skills": passive_skills,
                "profile_lore": profile_lore,
                "param_str": str_rank,
                "param_end": end_rank,
                "param_agi": agi_rank,
                "param_mna": mna_rank,
                "param_lck": lck_rank,
                "param_np": np_rank,
                "face_url": face_url,
                "art_stage1": art1,
                "art_stage2": art2,
                "art_stage3": art3,
                "art_stage4": art4,
            }

            _, created = Servant.objects.update_or_create(
                collection_no=collection_no,
                defaults=defaults
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"[SYSTEM OK] Database refreshed with Skills & Lore! Created: {created_count} | Updated: {updated_count}"
            )
        )