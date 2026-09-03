"""
Relecture automatique de l'édition dressée, avant publication.

Deuxième regard, indépendant de la rédaction (dresser.py) : un second appel
LLM applique la même grille de rigueur, mais en lecture seule — il ne
réécrit jamais le texte, il dit seulement si l'édition est publiable telle
quelle ou si elle doit partir en revue humaine. Rédaction et relecture
restent deux passes séparées, comme deux personnes différentes qui ne se
contentent pas de se relire elles-mêmes.

Ce module ne décide jamais seul de publier — c'est edition_builder.py qui
combine ce verdict avec le seuil de confiance du matcher pour choisir entre
publication automatique et mise en attente de validation humaine.
"""

import json
from anthropic import Anthropic
from mechanisms_pool import Mechanism

client = Anthropic()  # lit ANTHROPIC_API_KEY dans l'environnement

MODEL = "claude-opus-5"

AUDIT_SYSTEM_PROMPT = """Tu es le relecteur indépendant d'une édition déjà rédigée pour un jeu de compréhension du monde. Tu ne rédiges rien, tu vérifies uniquement.

On te donne : le mécanisme causal de référence (figé, jamais à remettre en cause), l'actualité réelle qui a servi de base (titre + résumé fournis au rédacteur), et le texte déjà rédigé (intro/situation/options) à auditer.

Grille de rigueur à vérifier point par point :

1. Un seul mécanisme causal isolé — le texte ne doit pas laisser croire que le mécanisme de référence est la seule explication possible de l'actualité citée, si d'autres facteurs indépendants pourraient aussi jouer.

2. Pas de sur-simplification qui rend l'énoncé faux — aucun verbe ou adverbe («automatiquement», «mécaniquement», «toujours»...) n'affirme une certitude systématique là où la réalité est une tendance ou un facteur parmi d'autres.

3. Séparation stricte fait sourcé / exemple illustratif — signale tout fait, chiffre ou citation attribué à une personne réelle qui n'est PAS présent dans le titre/résumé fourni (c'est le défaut le plus grave : un détail inventé qui a l'air d'un fait rapporté). Tout scénario ajouté au-delà des faits fournis doit être explicitement marqué comme illustratif (ex. "exemple illustratif" ou "Imaginons que...").

4. Format correct — situation courte et compréhensible, 3 options dont une seule clairement correcte et fidèle au mécanisme de référence.

Réponds uniquement en JSON valide, sans texte autour :
{"passed": bool, "issues": ["<un point précis par ligne, vide si aucun problème>"], "verdict": "publiable" | "a_revoir"}
"""


def audit_edition(mechanism: Mechanism, dressed: dict, headline) -> dict:
    user_prompt = json.dumps({
        "mecanisme_de_reference": {
            "label": mechanism.label,
            "explanation": mechanism.explanation,
            "cause_effect": mechanism.cause_effect,
            "type": mechanism.mechanism_type.value,
        },
        "actualite_reelle_fournie_au_redacteur": {
            "titre": headline.title,
            "resume": headline.summary,
            "source": headline.source,
        },
        "edition_dressee_a_auditer": {
            "intro": dressed.get("intro", ""),
            "situation": dressed.get("situation", ""),
            "options": dressed.get("options", []),
        },
    }, ensure_ascii=False)

    response = client.messages.create(
        model=MODEL,
        max_tokens=800,
        output_config={"effort": "medium"},  # relecture ciblée, pas une génération longue
        system=AUDIT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = next(b.text for b in response.content if b.type == "text").strip()
    if raw.startswith("```"):
        raw = raw.strip("`").removeprefix("json").strip()

    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        # Une relecture qui échoue à répondre proprement ne doit jamais
        # être interprétée comme un feu vert — on part en revue humaine.
        return {"passed": False, "issues": ["Relecture automatique : sortie JSON invalide"],
                "verdict": "a_revoir"}

    result.setdefault("passed", result.get("verdict") == "publiable")
    result.setdefault("issues", [])
    return result
