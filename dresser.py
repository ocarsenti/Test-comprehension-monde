"""
Habillage de la scène du jour.

Même principe que dresser.py du projet MDR : le LLM habille, il ne juge
jamais. `explanation` et `source` viennent toujours de mechanisms_pool.py
tels quels, jamais réécrits ici.

Pour un mécanisme DILEMMA, le LLM peut générer les options de la question
de risque, mais la bonne réponse (quelle option identifie correctement
le risque) doit être fournie séparément et validée avant publication —
jamais laissée au jugement du LLM seul.
"""

import os
import json
from anthropic import Anthropic
from mechanisms_pool import Mechanism, MechanismType

client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

DRESS_SYSTEM_PROMPT = """Tu habilles narrativement l'édition du jour d'un jeu de compréhension du monde.

Règles strictes :
- Le mécanisme, son explication et sa source te sont donnés — tu ne les modifies JAMAIS, tu les recopies tels quels dans ta sortie.
- Tu écris une situation courte (2-3 phrases) qui relie le mécanisme à l'actualité réelle fournie.
- Tu proposes 3 options de réponse : une correcte (fidèle au mécanisme), deux plausibles mais fausses.
- Toute suite ou conséquence que tu inventes au-delà des faits fournis doit être explicitement marquée comme illustrative, jamais présentée comme un fait vérifié.
- Réponds uniquement en JSON valide.

Format :
{"intro": "...", "situation": "...", "options": [{"id":"a","text":"...","correct":bool}, ...]}
"""


def dress_edition(mechanism: Mechanism, headline, reasoning: str) -> dict:
    user_prompt = json.dumps({
        "mecanisme": {
            "label": mechanism.label,
            "base_situation": mechanism.base_situation,
            "type": mechanism.mechanism_type.value,
        },
        "actualite_reelle": {
            "titre": headline.title,
            "resume": headline.summary,
            "source": headline.source,
        },
        "rattachement": reasoning,
    }, ensure_ascii=False)

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=600,
        system=DRESS_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    dressed = json.loads(response.content[0].text.strip())

    # Garde-fou : on écrase toujours explanation/source avec les valeurs
    # figées du pool, même si le LLM a tenté de les reformuler
    dressed["explanation"] = mechanism.explanation
    dressed["source"] = mechanism.source
    dressed["mechanism_id"] = mechanism.id
    dressed["mechanism_type"] = mechanism.mechanism_type.value

    return dressed
