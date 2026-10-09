import re

# Known Lv 10 signature steroid values with card-specific classifications
KNOWN_STEROIDS = {
    # Oberon
    "morning lark": {"atk": 0.0, "buster": 0.0, "arts": 0.0, "quick": 0.0, "np_dmg": 0.30},        # S1: +30% NP Dmg to Party
    
    # Castoria (Arts Meta)
    "charismatic vanguard": {"atk": 0.20, "buster": 0.0, "arts": 0.0, "quick": 0.0, "np_dmg": 0.0}, # S1: +20% ATK
    "lake protection": {"atk": 0.0, "buster": 0.0, "arts": 0.0, "quick": 0.0, "np_dmg": 0.0},
    "round of avalon": {"atk": 0.50, "buster": 0.0, "arts": 0.0, "quick": 0.0, "np_dmg": 0.30},    # NP: ATK + NP Dmg
    
    # Koyanskaya of Light (Buster Meta)
    "innovator of light": {"atk": 0.0, "buster": 0.0, "arts": 0.0, "quick": 0.0, "np_dmg": 0.0},
    "aptitude for slaughter (human)": {"atk": 0.0, "buster": 0.50, "arts": 0.0, "quick": 0.0, "np_dmg": 0.0}, # S3: +50% Buster
    
    # Summer Skadi / Skadi (Quick Meta)
    "primordial rune (ocean)": {"atk": 0.20, "buster": 0.0, "arts": 0.0, "quick": 0.50, "np_dmg": 0.0}, # S1/S2: +50% Quick, +20% ATK
    "primordial rune": {"atk": 0.0, "buster": 0.0, "arts": 0.0, "quick": 0.50, "np_dmg": 0.0},
    
    # Merlin (Buster Meta)
    "dreamlike charisma": {"atk": 0.20, "buster": 0.0, "arts": 0.0, "quick": 0.0, "np_dmg": 0.0},
    "hero creation": {"atk": 0.0, "buster": 0.50, "arts": 0.0, "quick": 0.0, "np_dmg": 0.0},        # S3: +50% Buster
    
    # Common Dual/Generic Skills
    "mana burst": {"atk": 0.0, "buster": 0.50, "arts": 0.0, "quick": 0.0, "np_dmg": 0.0},
    "voyager of the storm": {"atk": 0.17, "buster": 0.0, "arts": 0.0, "quick": 0.0, "np_dmg": 0.17},
    "military tactics": {"atk": 0.0, "buster": 0.0, "arts": 0.0, "quick": 0.0, "np_dmg": 0.20},
}


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

def extract_buff_values(skill_name, skill_detail):
    """
    Extracts steroid buffs from skill name and text.
    Separates card buffs into explicit buster, arts, and quick bins.
    """
    buffs = {"atk": 0.0, "buster": 0.0, "arts": 0.0, "quick": 0.0, "np_dmg": 0.0}
    name_clean = (skill_name or "").strip().lower()

    # 1. Match known signature skills
    for sig_name, val_map in KNOWN_STEROIDS.items():
        if sig_name in name_clean:
            return dict(val_map)

    if not skill_detail:
        return buffs

    detail = skill_detail.lower()
    matches = re.findall(r'(\d+)%', detail)
    default_val = (float(matches[0]) / 100.0) if matches else 0.20
    card_val = (float(matches[0]) / 100.0) if matches else 0.30

    # ATK buffs
    if "atk" in detail or "attack" in detail:
        buffs["atk"] += default_val

    # Specific Card Performance
    if "buster" in detail:
        buffs["buster"] += card_val
    if "arts" in detail:
        buffs["arts"] += card_val
    if "quick" in detail:
        buffs["quick"] += card_val
    if "card performance" in detail and not any(c in detail for c in ["buster", "arts", "quick"]):
        # Universal rainbow buff (e.g. Voyager of the Storm variants)
        buffs["buster"] += card_val
        buffs["arts"] += card_val
        buffs["quick"] += card_val

    # NP Damage Up
    np_dmg_triggers = ["np damage", "noble phantasm damage", "np strength", "increases np damage"]
    if any(t in detail for t in np_dmg_triggers):
        buffs["np_dmg"] += (float(matches[0]) / 100.0) if matches else 0.30

    return buffs

def analyze_frontline(servants, slot_configs=None, primary_slot=0):
    """
    Simulates Turn-1 tactical deployment with card color affinity gating.
    Only card buffs matching the Primary Carry's NP card type scale damage.
    """
    if slot_configs is None:
        slot_configs = [{'ce_np': 50, 'append2': False} for _ in range(len(servants))]

    telemetry = []
    party_battery_pool = 0
    target_battery_pool = 0

    # Aggregated raw buffs from all 3 members
    raw_buffs = {"atk": 0.0, "buster": 0.0, "arts": 0.0, "quick": 0.0, "np_dmg": 0.0}

    # Identify Primary Carry and their NP Card Type
    carry = servants[primary_slot] if (0 <= primary_slot < len(servants)) else (servants[0] if servants else None)
    carry_np_card = getattr(carry, 'np_card', 'Buster').capitalize() if carry else "Buster"
    carry_card_key = carry_np_card.lower()  # "buster", "arts", or "quick"

    for idx, s in enumerate(servants):
        cfg = slot_configs[idx] if idx < len(slot_configs) else {'ce_np': 0, 'append2': False}
        ce_charge = int(cfg.get('ce_np', 0))
        append_charge = 20 if cfg.get('append2', False) else 0
        base_starting_np = ce_charge + append_charge

        s_self = getattr(s, 'battery_self', 0) or 0
        party_battery_pool += (getattr(s, 'battery_party', 0) or 0)
        target_battery_pool += (getattr(s, 'battery_target', 0) or 0)

        # Extract kit buffs
        for sk in (s.active_skills or []):
            name = sk.get("name", "")
            detail = sk.get("detail", "")
            b = extract_buff_values(name, detail)

            raw_buffs["atk"] += b["atk"]
            raw_buffs["buster"] += b["buster"]
            raw_buffs["arts"] += b["arts"]
            raw_buffs["quick"] += b["quick"]
            raw_buffs["np_dmg"] += b["np_dmg"]

        telemetry.append({
            "servant": s,
            "self_battery": s_self,
            "ce_np": ce_charge,
            "append_np": append_charge,
            "party_received": 0,
            "target_received": 0,
            "starting_np": base_starting_np,
            "total_np": base_starting_np + s_self
        })

    # Distribute Party Batteries
    for item in telemetry:
        item["party_received"] = party_battery_pool
        item["total_np"] += party_battery_pool

    # Distribute Targeted Batteries to designated Primary Carry
    if 0 <= primary_slot < len(telemetry):
        telemetry[primary_slot]["target_received"] = target_battery_pool
        telemetry[primary_slot]["total_np"] += target_battery_pool

    for item in telemetry:
        item["np_ready"] = item["total_np"] >= 100
        item["gauge_fill_pct"] = min(item["total_np"], 100)

    # Card Affinity Matching:
    # Only card buffs matching carry_card_key will boost NP damage
    applicable_card_buff = raw_buffs.get(carry_card_key, 0.0)
    
    # Calculate non-effective/wasted card buffs for HUD telemetry diagnostics
    wasted_card_buffs = {k: v for k, v in raw_buffs.items() if k in ["buster", "arts", "quick"] and k != carry_card_key and v > 0}

    multiplicative_factor = (
        (1.0 + raw_buffs["atk"]) *
        (1.0 + applicable_card_buff) *
        (1.0 + raw_buffs["np_dmg"])
    )
    additive_factor = 1.0 + raw_buffs["atk"] + applicable_card_buff + raw_buffs["np_dmg"]
    multiplicative_gain_pct = (
        round(((multiplicative_factor - additive_factor) / additive_factor) * 100, 1)
        if additive_factor > 0 else 0.0
    )

    return {
        "slots": telemetry,
        "party_battery_pool": party_battery_pool,
        "target_battery_pool": target_battery_pool,
        "primary_slot": primary_slot,
        "carry_np_card": carry_np_card,
        "buffs": {
            "atk_pct": int(raw_buffs["atk"] * 100),
            "card_pct": int(applicable_card_buff * 100),
            "card_type": carry_np_card,
            "has_mismatch": len(wasted_card_buffs) > 0,
            "np_pct": int(raw_buffs["np_dmg"] * 100),
            "multiplier": round(multiplicative_factor, 2),
            "gain_vs_additive": multiplicative_gain_pct
        }
    }