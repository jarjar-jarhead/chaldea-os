import os
from google import genai
from google.genai import types

def format_kit(servant):
    skills = []
    for s in (servant.active_skills or [])[:3]:
        skills.append(f"- {s.get('name')}: {s.get('detail')}")

    passives = []
    for p in (servant.passive_skills or [])[:4]:
        passives.append(f"- {p.get('name')}: {p.get('detail')}")

    return {
        "skills": "\n".join(skills) if skills else "- No recorded active skills.",
        "passives": "\n".join(passives) if passives else "- No recorded passives.",
    }

def generate_tactical_debrief(servant_a, servant_b):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "// TACTICAL AI OFFLINE: GEMINI_API_KEY environment variable not detected."

    kit_a = format_kit(servant_a)
    kit_b = format_kit(servant_b)

    prompt = f"""
You are the CHALDEA TACTICAL OS combat analysis engine. Deliver a crisp, rapid tactical debrief comparing two Servants for deployment.

[ALPHA SUBJECT]
* Name: #{servant_a.collection_no:03d} {servant_a.name} ({servant_a.class_name})
* Base Stats: ATK {servant_a.atk_max} | HP {servant_a.hp_max} | Cost: {servant_a.cost}
* Deck: {servant_a.deck}
* Noble Phantasm: {servant_a.np_name} ({servant_a.np_card} / {servant_a.np_type})
  Effect: {servant_a.np_detail}
* Active Skills:
{kit_a['skills']}
* Passives:
{kit_a['passives']}

[BETA SUBJECT]
* Name: #{servant_b.collection_no:03d} {servant_b.name} ({servant_b.class_name})
* Base Stats: ATK {servant_b.atk_max} | HP {servant_b.hp_max} | Cost: {servant_b.cost}
* Deck: {servant_b.deck}
* Noble Phantasm: {servant_b.np_name} ({servant_b.np_card} / {servant_b.np_type})
  Effect: {servant_b.np_detail}
* Active Skills:
{kit_b['skills']}
* Passives:
{kit_b['passives']}

OUTPUT FORMAT RULES:
Use EXACTLY these three bold headers, with 2 concise bullet points under each:

**OPERATIONAL NICHE & ROLE**
* Alpha: [Concise primary role, e.g. multi-turn crit DPS, wave cleaner, or stall]
* Beta: [Concise primary role]

**KIT & SYNERGY DIFFERENTIAL**
* Battery & Steroids: [Compare charge % and buff uptimes]
* Survivability & Utility: [Compare invuln, guts, hard defense, or party support]

**TACTICAL DEPLOYMENT DIRECTIVE**
* Field Alpha when: [Specific boss / farming node condition]
* Field Beta when: [Specific boss / farming node condition]

Keep total length concise and under 180 words. Do not trail off or write unprompted commentary.
"""

    try:
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=3000,  # Uncapped runway
            ),
        )
        result = response.text.strip() if response.text else "// TELEMETRY VOID: Model returned empty response."
        print(f"[AI ENGINE] Success. Length: {len(result)} chars")
        return result
    except Exception as e:
        error_msg = f"// TELEMETRY TRANSMISSION ERROR: {str(e)}"
        print(f"[AI ENGINE] Error: {e}")
        return error_msg