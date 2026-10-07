import re


# Comprehensive registry of battery values for all meta supports & irregular charge values
KNOWN_SKILL_BATTERIES = {
    # 100% Batteries
    "ray horizon": (100, "self"),              # Mélusine S3
    "high-speed divine words": (100, "self"),  # Medea / Circe
    "rapid casting": (80, "self"),             # Avicebron / Paracelsus
    
    # Oberon
    "morning lark": (20, "party"),             # Oberon S1
    "lie-like dream": (50, "target"),          # Oberon S2
    
    # Merlin & Waver
    "dreamlike charisma": (30, "party"),       # Merlin S1
    "discerning eye": (30, "target"),          # Zhuge Liang (Waver) S1
    "tactician's advice": (10, "party"),       # Waver S2
    "tactician's command": (10, "party"),      # Waver S3
    
    # Castoria & Koyanskaya
    "charismatic vanguard": (20, "party"),     # Castoria S1
    "protection of the lake": (20, "party"),   # Castoria S2 (Party 20% + Target 30%)
    "innovator of light": (50, "target"),      # Koyanskaya S1
    
    # Skadi & Summer Skadi
    "primordial rune": (50, "target"),         # Skadi / Ruler Skadi S3
    
    # Common 50% & 30% Self Batteries
    "mana burst (flame)": (30, "self"),
    "dragon's pulse": (30, "self"),            # Mélusine S1
    "star of the heart": (50, "self"),         # Space Ishtar
    "golden rule (body)": (50, "self"),
    "animal dialogue": (50, "self"),           # Kintoki
    "witchcraft": (30, "self"),
    "philosophy key": (50, "self"),            # Aoko
}

def extract_battery_values(skill_name, skill_detail):
    """
    Extracts NP gauge charge percentage and scope.
    Matches known names first, then inspects Atlas detail text phrasing.
    """
    clean_name = (skill_name or "").strip().lower()

    # 1. Exact or partial match in signature dictionary
    for registered_name, (amount, scope) in KNOWN_SKILL_BATTERIES.items():
        if registered_name in clean_name:
            return amount, scope

    if not skill_detail:
        return 0, "none"

    text = skill_detail.lower()

    # 2. Determine target scope
    if any(k in text for k in ["party", "all allies", "all party members", "their np gauge"]):
        scope = "party"
    elif any(k in text for k in ["an ally", "target ally", "one ally", "chosen ally"]):
        scope = "target"
    else:
        scope = "self"

    # 3. Numeric regex fallback if explicit bracket [50%] exists
    match = re.search(r'(\d+)%', text)
    if match:
        return int(match.group(1)), scope

    # 4. Keyword heuristics for unindexed servants
    if "massively charges" in text or "greatly charges" in text:
        return 100 if scope == "self" else 50, scope

    if "charges" in text and "np gauge" in text:
        # Standard default FGO skill battery amounts
        if scope == "party":
            return 20, "party"
        if scope == "target":
            return 30, "target"
        return 30, "self"

    return 0, "none"

def extract_buff_values(skill_detail):
    """
    Extracts steroid buffs from skill text (ATK Up, Card Performance Up, NP Damage Up).
    """

    buffs = {"atk": 0.0, "card" : 0.0, "np_dmg" : 0.0}
    if not skill_detail:
        return buffs

    detail = skill_detail.lower()
    matches = re.findall(r'(\d+)%', detail)
    val = (float(matches[0])/ 100.0) if matches else 0.20 #got default fallback of 20%

    if "atk" in detail or "attack" in detail:
        buffs["atk"] += val
    if any( c in detail for c in ["buster", "arts", "quick", "card performance"]):
        buffs["card"] += val
    if "np damage" in detail or "noble phantasm damage" in detail:
        buffs["np_dmg"] += val

    return buffs

def analyze_frontline(servants, slot_configs=None, primary_slot=0):
    """
    Simulates Turn-1 tactical deployment with isolated CE values & Append 2 toggles.
    slot_configs: list of dicts, e.g. [{'ce_np': 50, 'append2': True}, ...]
    """
    if slot_configs is None:
        slot_configs = [{'ce_np': 50, 'append2': False} for _ in range(len(servants))]

    telemetry = []

    #Total battery pool available from the party
    party_battery_pool = 0
    target_battery_pool = 0

    #Global steroid accumulator for the primary carry
    total_buffs = {"atk": 0.0 , "card" : 0.0, "np_dmg" : 0.0}

    for idx, s in enumerate(servants):
        self_battery = 0
        cfg = slot_configs[idx] if idx < len(slot_configs) else {'ce_np': 0, 'append2': False}

        ce_charge = int(cfg.get('ce_np', 0))
        append_charge = 20 if cfg.get('append2', False) else 0
        base_starting_np = ce_charge + append_charge

        for sk in (s.active_skills or []):
            name = sk.get("name", "")
            detail = sk.get("detail", "")
            amt, scope = extract_battery_values(name, detail)

            if scope == "party":
                party_battery_pool += amt
            elif scope == "target":
                target_battery_pool += amt
            elif scope == "self":
                self_battery += amt

            b = extract_buff_values(detail)
            total_buffs["atk"] += b["atk"]
            total_buffs["card"] += b["card"]
            total_buffs["np_dmg"] += b["np_dmg"]

        telemetry.append({
            "servant": s,
            "self_battery": self_battery,
            "ce_np": ce_charge,
            "append_np": append_charge,
            "party_received": 0,
            "target_received": 0,
            "starting_np": base_starting_np,
            "total_np": base_starting_np + self_battery
        })

    # Distribute party charge to all 3 slots
    for item in telemetry:
        item["party_received"] = party_battery_pool
        item["total_np"] += party_battery_pool

    # Distribute targetable battery pool to the designated carry
    if 0 <= primary_slot < len(telemetry):
        telemetry[primary_slot]["target_received"] = target_battery_pool
        telemetry[primary_slot]["total_np"] += target_battery_pool

    # Update gauge readiness
    for item in telemetry:
        item["np_ready"] = item["total_np"] >= 100
        item["gauge_fill_pct"] = min(item["total_np"], 100)

    # Multiplicative Buff Scaling: (1 + ATK) * (1 + Card) * (1 + NP Damage)
    multiplicative_factor = (
        (1.0 + total_buffs["atk"]) *
        (1.0 + total_buffs["card"]) *
        (1.0 + total_buffs["np_dmg"])
    )
    additive_factor = 1.0 + total_buffs["atk"] + total_buffs["card"] + total_buffs["np_dmg"]
    multiplicative_gain_pct = (
        round(((multiplicative_factor - additive_factor) / additive_factor) * 100, 1)
        if additive_factor > 0 else 0.0
    )

    return {
        "slots": telemetry,
        "party_battery_pool": party_battery_pool,
        "target_battery_pool": target_battery_pool,
        "primary_slot": primary_slot,
        "buffs": {
            "atk_pct": int(total_buffs["atk"] * 100),
            "card_pct": int(total_buffs["card"] * 100),
            "np_pct": int(total_buffs["np_dmg"] * 100),
            "multiplier": round(multiplicative_factor, 2),
            "gain_vs_additive": multiplicative_gain_pct
        }
    }