import { useEffect, useRef, useState } from "react";
import { MechanismGlobe, type MechanismGlobeHandle } from "./MechanismGlobe/MechanismGlobe";
import { buildMockPool, addMockMechanisms } from "./mockData/mechanismPool";
import { loadRealMechanismPool } from "./realData";
import { CATEGORY_COLORS } from "./MechanismGlobe/colors";
import { loadCountries } from "./MechanismGlobe/geo";
import { clusterCountries } from "./MechanismGlobe/clustering";
import type { MechanismEntry } from "./MechanismGlobe/types";

function clusterStats(pool: MechanismEntry[]) {
  const countries = loadCountries();
  const clusters = clusterCountries(countries, pool.length);
  const weights = clusters.map(c => c.totalWeight);
  const min = Math.min(...weights);
  const max = Math.max(...weights);
  return {
    zoneCount: clusters.length,
    countryCount: countries.length,
    minWeight: min,
    maxWeight: max,
    balanceRatio: max / min,
  };
}

const isEmbed = new URLSearchParams(window.location.search).has("embed");

/**
 * Mode ?embed=1 : rendu épuré pour intégration en iframe dans l'onglet
 * "Carte mentale" de la démo principale — pas de panneau de contrôle de
 * démo, juste le globe + la légende catégories, fond identique pour ne
 * laisser voir aucun cadre.
 *
 * Charge le VRAI pool (mechanism_pool.json, exporté depuis
 * mechanisms_pool.py) fusionné avec le vrai historique de l'utilisateur
 * (localStorage cm_history, partagé car même origine que la démo).
 */
function EmbedApp() {
  const [pool, setPool] = useState<MechanismEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadRealMechanismPool()
      .then(setPool)
      .catch(e => setError(String(e?.message ?? e)));
  }, []);

  if (error) {
    return (
      <div style={{ width: "100%", height: "100vh", background: "#ffffff", color: "#1c2b3a", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "system-ui, sans-serif", fontSize: 13, padding: 20, textAlign: "center" }}>
        Pool de mécanismes indisponible ({error}).
      </div>
    );
  }
  if (!pool) return <div style={{ width: "100%", height: "100vh", background: "#ffffff" }} />;

  return (
    <div style={{ width: "100%", height: "100vh", background: "#ffffff" }}>
      <MechanismGlobe mechanismPool={pool} />
    </div>
  );
}

function DevHarness() {
  const [pool, setPool] = useState<MechanismEntry[]>(() => buildMockPool(58));
  const [log, setLog] = useState<string[]>([]);
  const globeRef = useRef<MechanismGlobeHandle>(null);

  function pushLog(line: string) {
    setLog(prev => [line, ...prev].slice(0, 8));
  }

  function handleAddTwo() {
    const before = clusterStats(pool);
    const next = addMockMechanisms(pool, 2);
    const after = clusterStats(next);
    setPool(next);
    pushLog(
      `Ajout de 2 mécanismes : ${before.zoneCount} -> ${after.zoneCount} zones ` +
        `(${after.countryCount} pays répartis, ratio max/min de surface ${after.balanceRatio.toFixed(2)}×).`
    );
  }

  function handleMasterRandom() {
    const candidates = pool.filter(m => m.state !== "mastered");
    if (candidates.length === 0) return;
    const pick = candidates[Math.floor(Math.random() * candidates.length)];
    globeRef.current?.setZoneState(pick.id, "mastered");
    setPool(prev => prev.map(m => (m.id === pick.id ? { ...m, state: "mastered" } : m)));
    pushLog(`« ${pick.label} » (${pick.category}) passe à l'état maîtrisé.`);
  }

  function handleEncounterRandom() {
    const candidates = pool.filter(m => m.state === "undiscovered");
    if (candidates.length === 0) return;
    const pick = candidates[Math.floor(Math.random() * candidates.length)];
    globeRef.current?.setZoneState(pick.id, "encountered");
    setPool(prev => prev.map(m => (m.id === pick.id ? { ...m, state: "encountered" } : m)));
    pushLog(`« ${pick.label} » (${pick.category}) passe à l'état rencontré.`);
  }

  const stats = clusterStats(pool);

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh", background: "#0a0c12", color: "#e7e9ee", fontFamily: "system-ui, sans-serif" }}>
      <header style={{ padding: "14px 20px", borderBottom: "1px solid #1e222c" }}>
        <h1 style={{ margin: 0, fontSize: 18 }}>MechanismGlobe — démo</h1>
        <p style={{ margin: "6px 0 0", fontSize: 13, color: "#9aa0ac" }}>
          {pool.length} mécanismes dans le pool {'→'} {stats.zoneCount} zones sur {stats.countryCount} pays
          (déséquilibre max/min : {stats.balanceRatio.toFixed(2)}×)
        </p>
      </header>

      <div style={{ display: "flex", flex: 1, minHeight: 0 }}>
        <div style={{ flex: 1, position: "relative" }}>
          <MechanismGlobe ref={globeRef} mechanismPool={pool} />
        </div>

        <aside style={{ width: 300, borderLeft: "1px solid #1e222c", padding: 16, overflowY: "auto" }}>
          <button style={btn} onClick={handleAddTwo}>Ajouter 2 mécanismes</button>
          <button style={btn} onClick={handleEncounterRandom}>Marquer "rencontré" (aléatoire)</button>
          <button style={btn} onClick={handleMasterRandom}>Marquer "maîtrisé" (aléatoire)</button>

          <h3 style={{ fontSize: 13, marginTop: 20 }}>Légende — catégories</h3>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {Object.entries(CATEGORY_COLORS).map(([cat, color]) => (
              <div key={cat} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
                <span style={{ width: 12, height: 12, borderRadius: "50%", background: color, flexShrink: 0 }} />
                {cat}
              </div>
            ))}
          </div>

          <h3 style={{ fontSize: 13, marginTop: 20 }}>Journal</h3>
          <ul style={{ fontSize: 12, color: "#9aa0ac", paddingLeft: 16 }}>
            {log.map((l, i) => (
              <li key={i} style={{ marginBottom: 8 }}>{l}</li>
            ))}
          </ul>
        </aside>
      </div>
    </div>
  );
}

export default function App() {
  return isEmbed ? <EmbedApp /> : <DevHarness />;
}

const btn: React.CSSProperties = {
  display: "block",
  width: "100%",
  marginBottom: 10,
  padding: "10px 12px",
  background: "#1c2030",
  border: "1px solid #2a2e3e",
  borderRadius: 10,
  color: "#e7e9ee",
  fontSize: 13,
  cursor: "pointer",
};
