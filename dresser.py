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

import json
from anthropic import Anthropic
from mechanisms_pool import Mechanism, MechanismType

client = Anthropic()  # lit ANTHROPIC_API_KEY dans l'environnement

MODEL = "claude-opus-5"

DRESS_SYSTEM_PROMPT = """Tu habilles narrativement l'édition du jour d'un jeu de compréhension du monde.

Règles strictes :
- Le mécanisme, son explication et sa source te sont donnés — tu ne les modifies JAMAIS, tu les recopies tels quels dans ta sortie.
- Tu écris une situation courte (2-3 phrases) qui relie le mécanisme à l'actualité réelle fournie.
- Tu proposes 3 options de réponse : une correcte (fidèle au mécanisme), deux plausibles mais fausses.
- Réponds uniquement en JSON valide.

Grille de rigueur, à appliquer à CHAQUE édition que tu rédiges :

1. Un seul mécanisme causal, jamais plusieurs causes indépendantes mélangées.
   Ne présente pas le mécanisme fourni comme LA seule explication possible de
   l'actualité si d'autres facteurs indépendants pourraient aussi jouer :
   reste centré sur le rouage précis illustré, sans laisser entendre qu'il
   est l'unique cause de tout ce qui se passe dans l'actualité citée.

2. Pas de sur-simplification qui rend l'énoncé faux. N'invente et n'affirme
   jamais comme une certitude mécanique et systématique quelque chose qui,
   en réalité, est une tendance, une possibilité, ou un facteur parmi
   d'autres — y compris dans les options de réponse. En cas de doute,
   préfère « peut » ou « tend à » à un verbe qui affirme une conséquence
   automatique.

3. Ne cite AUCUN fait, chiffre, citation ou déclaration attribuée à une
   personne réelle qui n'est pas explicitement présent dans le titre ou le
   résumé de l'actualité qui t'est fournie. Tu peux reformuler et
   contextualiser, jamais inventer un détail factuel supplémentaire
   (citation, chiffre précis, déclaration) qui n'y figure pas. Toute mise en
   situation, tout scénario ou toute suite que tu ajoutes au-delà des faits
   fournis doit être introduit par une formule explicite du type « Imaginons
   que... » et porter la mention « (exemple illustratif) » — jamais présenté
   comme un fait rapporté par la source. Un lecteur doit toujours pouvoir
   distinguer en une lecture ce qui vient de l'actualité réelle citée de ce
   que tu as inventé pour illustrer.

4. Structure attendue : `intro` situe le mécanisme et cite la source réelle
   (nom du média + titre de l'article tel que fourni, pour rester
   vérifiable) ; `situation` relie ce fait réel au mécanisme, en isolant
   clairement toute partie illustrative selon la règle 3 ; les `options`
   testent la compréhension du mécanisme, pas la mémorisation de détails
   d'actualité annexes.

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
        model=MODEL,
        max_tokens=1200,
        output_config={"effort": "medium"},  # habillage narratif court, pas besoin de "high"
        system=DRESS_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = next(b.text for b in response.content if b.type == "text").strip()
    if raw.startswith("```"):
        raw = raw.strip("`").removeprefix("json").strip()
    dressed = json.loads(raw)

    # Garde-fou : on écrase toujours explanation/source avec les valeurs
    # figées du pool, même si le LLM a tenté de les reformuler
    dressed["explanation"] = mechanism.explanation
    dressed["source"] = mechanism.source
    dressed["mechanism_id"] = mechanism.id
    dressed["mechanism_type"] = mechanism.mechanism_type.value

    return dressed
