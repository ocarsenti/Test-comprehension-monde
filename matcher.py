"""
Rapprochement actualité → mécanisme.

CE QUE CE FICHIER A LE DROIT DE FAIRE :
- Choisir, parmi les mécanismes du pool, celui qui correspond le mieux
  à une actualité du jour
- Donner un score de confiance sur ce choix

CE QU'IL N'A JAMAIS LE DROIT DE FAIRE :
- Inventer un nouveau mécanisme qui n'existe pas dans le pool
- Décider tout seul qu'un rattachement fragile est publiable —
  c'est le seuil de confiance (contrôlé en code, pas par le LLM
  lui-même) qui tranche
"""

import json
from anthropic import Anthropic
from mechanisms_pool import FULL_POOL, Mechanism

client = Anthropic()  # lit ANTHROPIC_API_KEY dans l'environnement

MODEL = "claude-opus-5"

CONFIDENCE_THRESHOLD = 0.7  # en dessous, la scène part en revue humaine

MATCH_SYSTEM_PROMPT = """Tu rapproches une liste de titres d'actualité d'un pool fixe de mécanismes causaux.

Règles strictes :
- Tu choisis UNIQUEMENT parmi les mécanismes fournis. Tu ne dois JAMAIS en inventer un nouveau.
- Si aucun mécanisme ne correspond raisonnablement, réponds avec mechanism_id: null.
- Ton score de confiance doit refléter honnêtement l'incertitude — ne force jamais un rattachement fragile pour avoir une réponse.
- Priorise, à qualité de rattachement égale : (1) un mécanisme déjà rencontré par les joueurs mais pas encore "maîtrisé" (réactivation), (2) un mécanisme "hub" à fort potentiel de connexion.

Réponds uniquement en JSON valide :
{"headline_index": <int>, "mechanism_id": "<id ou null>", "confidence": <0.0-1.0>, "reasoning": "<une phrase>"}
"""


def match_headlines_to_mechanism(headlines: list, pool: list[Mechanism] = FULL_POOL,
                                   already_encountered_ids: set = None) -> dict:
    """Reçoit les titres du jour, renvoie le meilleur rattachement trouvé
    (ou None si rien ne dépasse le seuil de confiance)."""

    pool_summary = [
        {"id": m.id, "label": m.label, "base_situation": m.base_situation,
         "category": m.category.value,
         "deja_rencontre": already_encountered_ids and m.id in already_encountered_ids}
        for m in pool
    ]
    headlines_summary = [
        {"index": i, "title": h.title, "summary": h.summary, "source": h.source}
        for i, h in enumerate(headlines)
    ]

    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        output_config={"effort": "low"},  # simple classification, pas besoin de raisonnement profond
        system=MATCH_SYSTEM_PROMPT,
        messages=[{
            "role": "user",
            "content": json.dumps({"mecanismes_disponibles": pool_summary, "titres_du_jour": headlines_summary},
                                    ensure_ascii=False),
        }],
    )

    raw = next(b.text for b in response.content if b.type == "text").strip()
    if raw.startswith("```"):
        raw = raw.strip("`").removeprefix("json").strip()
    result = json.loads(raw)

    # Garde-fou : un mechanism_id halluciné (hors pool) est rejeté ici,
    # jamais fait confiance aveuglément
    if result.get("mechanism_id"):
        valid_ids = {m.id for m in pool}
        if result["mechanism_id"] not in valid_ids:
            return {"matched": False, "reason": "mechanism_id hors pool — halluciné, rejeté"}

    if not result.get("mechanism_id") or result.get("confidence", 0) < CONFIDENCE_THRESHOLD:
        return {"matched": False, "reason": "aucun candidat au-dessus du seuil de confiance", "raw": result}

    return {
        "matched": True,
        "headline": headlines[result["headline_index"]],
        "mechanism_id": result["mechanism_id"],
        "confidence": result["confidence"],
        "reasoning": result["reasoning"],
    }
