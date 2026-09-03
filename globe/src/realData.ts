import type { Encounter, MechanismEntry, ZoneState } from "./MechanismGlobe/types";

/**
 * Clé localStorage écrite par test-comprehension-mondev.html
 * (fonction recordConsultation) — partagée car le globe est servi sous
 * /globe/ sur le MÊME domaine que la démo, donc même origine = même
 * localStorage, sans avoir besoin de postMessage.
 */
const HISTORY_KEY = "cm_history";

interface RawPoolMechanism {
  id: string;
  category: string;
  label: string;
  cause_effect?: string;
}

interface HistoryEntry {
  label: string;
  category: string;
  cause_effect?: string;
  encounters: Encounter[];
}

function readHistory(): Record<string, HistoryEntry> {
  try {
    const raw = window.localStorage.getItem(HISTORY_KEY);
    return raw ? JSON.parse(raw) : {};
  } catch {
    return {};
  }
}

function stateFromEncounterCount(n: number): ZoneState {
  if (n >= 3) return "mastered";
  if (n >= 1) return "encountered";
  return "undiscovered";
}

/**
 * Charge le vrai pool (exporté par export_mechanism_pool.py depuis
 * mechanisms_pool.py) et le fusionne avec l'historique réel de
 * l'utilisateur (cm_history) pour produire l'état de chaque zone.
 */
export async function loadRealMechanismPool(): Promise<MechanismEntry[]> {
  const res = await fetch("mechanism_pool.json", { cache: "no-store" });
  if (!res.ok) throw new Error(`mechanism_pool.json introuvable (${res.status})`);
  const data = (await res.json()) as { mechanisms: RawPoolMechanism[] };

  const history = readHistory();

  return data.mechanisms.map(m => {
    const h = history[m.id];
    const encounters = h?.encounters ?? [];
    return {
      id: m.id,
      category: m.category,
      label: m.label,
      state: stateFromEncounterCount(encounters.length),
      encounters,
    };
  });
}
