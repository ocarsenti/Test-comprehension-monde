"""
Construction de l'édition du jour — orchestre les trois briques
(rss_sources, matcher, dresser) sans jamais leur faire dépasser leur
rôle : collecte gratuite, jugement de rattachement, habillage narratif.

MULTI-UTILISATEUR : l'édition du jour est calculée UNE FOIS, partagée
par tout le monde (c'est elle qui reste bon marché). La progression
(qui a rencontré quoi, quand) est strictement individuelle — deux
tables séparées, jamais mélangées. Un joueur qui rejoint en cours de
route ne dépend jamais de l'historique des autres.
"""

import json
from datetime import datetime, date

from rss_sources import fetch_todays_headlines
from matcher import match_headlines_to_mechanism
from dresser import dress_edition
from mechanisms_pool import get_mechanism, FULL_POOL

# En prod : remplacer ces deux fichiers par de vraies tables (Postgres...)
SHARED_EDITIONS_FILE = "editions_partagees.json"     # une par jour, pour tous
USER_PROGRESS_FILE = "progression_utilisateurs.json"  # une entrée par joueur

# Fichier public, lu directement par test-comprehension-mondev.html — ne
# contient jamais de données de progression individuelle, seulement les
# éditions fraîches les plus récentes (format "démo enchaînée").
PUBLIC_EDITION_FILE = "edition_comprehension_monde.json"
MAX_PUBLIC_QUESTIONS = 6
ANALYST_PRESENTERS = ["Véronica", "Dan"]  # alterne, John reste toujours le rapporteur


def load_user_progress(user_id: str) -> dict:
    try:
        with open(USER_PROGRESS_FILE) as f:
            all_users = json.load(f)
    except FileNotFoundError:
        all_users = {}
    return all_users.get(user_id, {"encounters": {}, "streak": 0, "last_active": None})


def save_user_progress(user_id: str, progress: dict):
    try:
        with open(USER_PROGRESS_FILE) as f:
            all_users = json.load(f)
    except FileNotFoundError:
        all_users = {}
    all_users[user_id] = progress
    with open(USER_PROGRESS_FILE, "w") as f:
        json.dump(all_users, f, ensure_ascii=False, indent=2)


def mastery_level(progress: dict, mechanism_id: str) -> str:
    dates = progress["encounters"].get(mechanism_id, [])
    if len(dates) >= 3:
        return "maîtrisé"
    if len(dates) >= 1:
        return "rencontré"
    return "inconnu"


def record_encounter(progress: dict, mechanism_id: str):
    today = date.today().isoformat()
    dates = progress["encounters"].setdefault(mechanism_id, [])
    if today not in dates:
        dates.append(today)


def build_shared_edition_of_the_day() -> dict:
    """Appelé UNE FOIS par jour, par une tâche planifiée — jamais par
    utilisateur. C'est cette édition, une fois construite, qui est
    ensuite servie à tout le monde."""
    try:
        with open(SHARED_EDITIONS_FILE) as f:
            editions = json.load(f)
    except FileNotFoundError:
        editions = {}

    today = date.today().isoformat()
    if today in editions:
        return editions[today]  # déjà générée aujourd'hui, on ne repaie pas l'IA deux fois

    try:
        headlines = fetch_todays_headlines()
        if not headlines:
            edition = {"type": "aucune", "reason": "Aucune actualité fraîche collectée"}
        else:
            match = match_headlines_to_mechanism(headlines, FULL_POOL)
            if not match["matched"]:
                edition = {"type": "aucune", "reason": match["reason"]}
            else:
                mechanism = get_mechanism(match["mechanism_id"])
                dressed = dress_edition(mechanism, match["headline"], match["reasoning"])
                edition = {
                    "date": today, "type": "fraîche", "mechanism_id": mechanism.id,
                    "confidence": match["confidence"], "edition": dressed,
                }
    except Exception as e:
        # Flux RSS en panne, quota API dépassé, JSON malformé... un jour
        # creux ne doit jamais faire planter la tâche planifiée ni écraser
        # l'historique déjà construit.
        edition = {"type": "aucune", "reason": f"Erreur pipeline : {e}"}

    editions[today] = edition
    with open(SHARED_EDITIONS_FILE, "w") as f:
        json.dump(editions, f, ensure_ascii=False, indent=2, default=str)

    export_public_edition(editions)
    return edition


def export_public_edition(editions: dict, max_questions: int = MAX_PUBLIC_QUESTIONS):
    """Reconstruit le fichier public consommé par test-comprehension-mondev.html
    à partir des dernières éditions 'fraîches' (les jours 'aucune'/'révision'
    n'ont pas de contenu dressé à montrer et sont ignorés ici)."""
    fresh_days = sorted(
        (day for day, ed in editions.items() if ed.get("type") == "fraîche"),
        reverse=True,
    )[:max_questions]

    questions = []
    for i, day in enumerate(reversed(fresh_days)):  # ordre chronologique pour la démo
        ed = editions[day]
        mechanism = get_mechanism(ed["mechanism_id"])
        dressed = ed["edition"]
        neighbor_labels = [
            {"id": nid, "label": n.label}
            for nid in mechanism.connects_to
            if (n := get_mechanism(nid)) is not None
        ]
        questions.append({
            "date": day,
            "mechanism_id": mechanism.id,
            "category": mechanism.category.value,
            "type": mechanism.mechanism_type.value,
            "presenter_ask": "John",
            "presenter_answer": ANALYST_PRESENTERS[i % len(ANALYST_PRESENTERS)],
            "situation": dressed.get("situation") or dressed.get("intro", ""),
            "options": dressed["options"],
            "explanation": mechanism.explanation,
            "source": mechanism.source,
            "mechanism_label": mechanism.label,
            "connects_to": neighbor_labels,
        })

    public = {"generated_at": datetime.now().isoformat(), "questions": questions}
    with open(PUBLIC_EDITION_FILE, "w") as f:
        json.dump(public, f, ensure_ascii=False, indent=2)
    return public


def get_edition_for_user(user_id: str) -> dict:
    """C'est CETTE fonction que l'appli mobile appelle, pour un joueur
    précis. Elle ne relance jamais l'IA — elle lit l'édition déjà
    construite pour aujourd'hui, et y ajoute le contexte propre à ce
    joueur (a-t-il déjà rencontré ce mécanisme, combien de fois)."""
    shared_edition = build_shared_edition_of_the_day()
    progress = load_user_progress(user_id)

    if shared_edition.get("type") != "fraîche":
        return fallback_revision_edition(user_id, progress, shared_edition.get("reason", ""))

    mechanism_id = shared_edition["mechanism_id"]
    return {
        **shared_edition,
        "mastery_before_for_this_user": mastery_level(progress, mechanism_id),
    }


def submit_answer(user_id: str, mechanism_id: str):
    """Appelé quand CE joueur a répondu — met à jour uniquement sa
    propre progression, jamais celle des autres."""
    progress = load_user_progress(user_id)
    record_encounter(progress, mechanism_id)
    progress["last_active"] = date.today().isoformat()
    save_user_progress(user_id, progress)
    return {"mastery_after": mastery_level(progress, mechanism_id)}


def fallback_revision_edition(user_id: str, progress: dict, reason: str) -> dict:
    """Jour creux CÔTÉ UTILISATEUR : chaque joueur peut avoir un
    mécanisme différent à réviser, puisque chacun a sa propre liste de
    mécanismes 'rencontrés mais pas maîtrisés'."""
    candidates = [mid for mid, dates in progress["encounters"].items() if 1 <= len(dates) < 3]
    if not candidates:
        return {"type": "aucune", "reason": reason}

    mechanism = get_mechanism(candidates[0])
    return {
        "type": "révision", "reason": reason, "mechanism_id": mechanism.id,
        "mastery_before_for_this_user": mastery_level(progress, mechanism.id),
        "note": "Pas d'actualité fraîche fiable aujourd'hui — révision d'un mécanisme que TU as déjà rencontré.",
    }


if __name__ == "__main__":
    # Simule deux joueurs différents, avec des historiques différents,
    # sur la même édition du jour
    edition_alice = get_edition_for_user("alice")
    print("Alice :", json.dumps(edition_alice, ensure_ascii=False, indent=2, default=str))

    edition_bob = get_edition_for_user("bob")
    print("Bob :", json.dumps(edition_bob, ensure_ascii=False, indent=2, default=str))
