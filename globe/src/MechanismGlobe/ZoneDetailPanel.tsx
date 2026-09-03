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
    background: "rgba(28,43,58,0.45)",
    display: "flex",
    alignItems: "flex-end",
    justifyContent: "center",
    zIndex: 50,
  },
  panel: {
    background: "#ffffff",
    color: "#1c2b3a",
    width: "100%",
    maxWidth: 560,
    maxHeight: "78vh",
    overflowY: "auto",
    borderRadius: "20px 20px 0 0",
    padding: "20px 20px 26px",
    fontFamily: "system-ui, sans-serif",
    boxShadow: "0 -8px 30px rgba(28,43,58,0.15)",
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
  title: { margin: 0, fontSize: 18, fontWeight: 800, color: "#1c2b3a" },
  close: { background: "none", border: "none", color: "#64748b", fontSize: 24, cursor: "pointer" },
  hint: { color: "#64748b", fontSize: 13, margin: "10px 0 16px" },
  mastered: { color: "#0e7a45", fontSize: 13, fontWeight: 700, margin: "10px 0 16px" },
  card: {
    background: "#f4f6fa",
    border: "1px solid #d9e1ea",
    borderRadius: 14,
    padding: "12px 16px",
    marginBottom: 12,
  },
  date: { display: "block", fontSize: 11, fontWeight: 700, color: "#b6792a", marginBottom: 6 },
  situation: { fontSize: 13, fontWeight: 700, margin: "0 0 6px", color: "#1c2b3a" },
  explain: { fontSize: 13, margin: "0 0 6px", color: "#475569" },
  source: { fontSize: 11, margin: 0, color: "#64748b", fontStyle: "italic" },
};
