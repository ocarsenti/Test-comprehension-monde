import type { MechanismEntry, ZoneState } from "../MechanismGlobe/types";

const CATEGORIES = [
  "économique",
  "institutionnel",
  "commerce",
  "démographie/migration",
  "géopolitique",
  "géologique/climatique",
  "vulnérabilité",
  "biologique",
  "écologique",
  "technologique",
  "psychologique",
  "juridique",
];

const LABELS = [
  "Choc matière première", "Répercussion d'un droit de douane", "Relèvement des taux directeurs",
  "Nominal vs réel", "Revalorisation automatique du SMIC", "Coût de la dette souveraine",
  "Vote en trilogue", "Guerre commerciale", "Indépendance de la banque centrale",
  "Effet de ricochet des sanctions", "Arbitrage entre puissances rivales", "Clause de défense collective",
  "Sécheresse récurrente", "Variabilité de la mousson", "Îlot de chaleur urbain",
  "Vieillissement démographique", "Viralité de la désinformation", "Dilemme du prisonnier climatique",
  "Externalité négative", "Bien commun et tragédie", "Asymétrie d'information",
  "Effet de réseau", "Rendement décroissant", "Cycle du crédit",
  "Prime de risque", "Aléa moral", "Course aux armements",
  "Dépendance de sentier", "Effet de levier", "Contagion financière",
  "Rente de situation", "Capture réglementaire", "Fenêtre d'opportunité politique",
  "Polarisation sociale", "Biais de confirmation", "Effet de halo médiatique",
  "Résistance aux antibiotiques", "Immunité de groupe", "Espèce invasive",
  "Point de bascule écologique", "Épuisement d'une ressource commune", "Innovation de rupture",
  "Cybersécurité en cascade", "Fracture numérique", "Vide juridique",
  "Extraterritorialité du droit", "Souveraineté numérique", "Réfugié climatique",
  "Fuite des cerveaux", "Dividende démographique", "Trappe à pauvreté",
];

function mulberry32(seed: number) {
  let a = seed;
  return function () {
    a |= 0;
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function mockEncounters(n: number, label: string) {
  const dates = ["2026-07-12", "2026-08-03", "2026-08-29"].slice(0, n);
  return dates.map(date => ({
    date,
    situation: `Une actualité illustrant « ${label} » (exemple mocké pour la démo, ${date}).`,
    explanation: `Explication canonique du mécanisme « ${label} », telle qu'affichée le ${date}.`,
    source: "Source d'exemple (démo).",
  }));
}

export function buildMockPool(count = 50): MechanismEntry[] {
  const rng = mulberry32(42);
  const pool: MechanismEntry[] = [];
  for (let i = 0; i < count; i++) {
    const category = CATEGORIES[i % CATEGORIES.length];
    const label = LABELS[i % LABELS.length] + (i >= LABELS.length ? ` (${i})` : "");
    const roll = rng();
    let state: ZoneState = "undiscovered";
    let encounterCount = 0;
    if (roll > 0.75) {
      state = "mastered";
      encounterCount = 3;
    } else if (roll > 0.45) {
      state = "encountered";
      encounterCount = roll > 0.6 ? 2 : 1;
    }
    pool.push({
      id: `mech_${i}`,
      category,
      label,
      state,
      encounters: encounterCount > 0 ? mockEncounters(encounterCount, label) : [],
    });
  }
  return pool;
}

export function addMockMechanisms(pool: MechanismEntry[], n: number): MechanismEntry[] {
  const rng = mulberry32(pool.length + 7);
  const extra: MechanismEntry[] = Array.from({ length: n }, (_, i) => {
    const idx = pool.length + i;
    const category = CATEGORIES[Math.floor(rng() * CATEGORIES.length)];
    return {
      id: `mech_${idx}`,
      category,
      label: `Nouveau mécanisme #${idx}`,
      state: "undiscovered" as ZoneState,
      encounters: [],
    };
  });
  return [...pool, ...extra];
}
