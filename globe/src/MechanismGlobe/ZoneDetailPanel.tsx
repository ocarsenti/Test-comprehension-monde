import type { MechanismEntry } from "./types";
import { categoryColor } from "./colors";

export function ZoneDetailPanel({
  mechanism,
  onClose,
}: {
  mechanism: MechanismEntry;
  onClose: () => void;
}) {
  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.panel} onClick={e => e.stopPropagation()}>
        <div style={styles.header}>
          <div>
            <span style={{ ...styles.tag, background: categoryColor(mechanism.category) }}>
              {mechanism.category}
            </span>
            <h3 style={styles.title}>{mechanism.label}</h3>
          </div>
          <button style={styles.close} onClick={onClose} aria-label="Fermer">
            ×
          </button>
        </div>

        {mechanism.state === "encountered" && (
          <p style={styles.hint}>
            Rencontré {mechanism.encounters?.length ?? 1} fois — encore {3 - (mechanism.encounters?.length ?? 1)} réactivation(s) espacée(s) avant maîtrise.
          </p>
        )}
        {mechanism.state === "mastered" && <p style={styles.mastered}>Mécanisme maîtrisé ✓</p>}

        {mechanism.encounters && mechanism.encounters.length > 0 ? (
          <div>
            {[...mechanism.encounters].reverse().map((e, i) => (
              <div key={i} style={styles.card}>
                <span style={styles.date}>{e.date}</span>
                <p style={styles.situation}>{e.situation}</p>
                <p style={styles.explain}>{e.explanation}</p>
                <p style={styles.source}>Source : {e.source}</p>
              </div>
            ))}
          </div>
        ) : (
          <p style={styles.hint}>Pas encore d'historique détaillé pour ce mécanisme.</p>
        )}
      </div>
    </div>
  );
}

const styles: Record<string, React.CSSProperties> = {
  overlay: {
    position: "fixed",
    inset: 0,
    background: "rgba(10,12,18,0.55)",
    display: "flex",
    alignItems: "flex-end",
    justifyContent: "center",
    zIndex: 50,
  },
  panel: {
    background: "#12141c",
    color: "#e7e9ee",
    width: "100%",
    maxWidth: 560,
    maxHeight: "78vh",
    overflowY: "auto",
    borderRadius: "20px 20px 0 0",
    padding: "20px 20px 26px",
    fontFamily: "system-ui, sans-serif",
  },
  header: { display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 },
  tag: {
    display: "inline-block",
    fontSize: 11,
    fontWeight: 700,
    color: "#fff",
    borderRadius: 999,
    padding: "3px 10px",
    marginBottom: 8,
  },
  title: { margin: 0, fontSize: 18, fontWeight: 800 },
  close: { background: "none", border: "none", color: "#aaa", fontSize: 24, cursor: "pointer" },
  hint: { color: "#a9adb8", fontSize: 13, margin: "10px 0 16px" },
  mastered: { color: "#5bd68a", fontSize: 13, fontWeight: 700, margin: "10px 0 16px" },
  card: {
    background: "#1b1e29",
    border: "1px solid #2a2e3a",
    borderRadius: 14,
    padding: "12px 16px",
    marginBottom: 12,
  },
  date: { display: "block", fontSize: 11, fontWeight: 700, color: "#8fa3ff", marginBottom: 6 },
  situation: { fontSize: 13, fontWeight: 700, margin: "0 0 6px", color: "#e7e9ee" },
  explain: { fontSize: 13, margin: "0 0 6px", color: "#b7bac2" },
  source: { fontSize: 11, margin: 0, color: "#8a8d96", fontStyle: "italic" },
};
