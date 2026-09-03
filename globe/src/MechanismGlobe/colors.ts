/**
 * Palette catégorielle — méthode du skill dataviz (OKLCH, jamais à l'œil).
 *
 * Les 8 premières teintes sont le jeu documenté et validé (adjacent CVD ΔE
 * >= 8, plancher vision normale >= 15, dans les deux modes). Les 4 dernières
 * ont été calculées avec la même méthode (angle de teinte OKLCH placé dans le
 * plus grand espace vide de la roue, luminosité/chroma interpolées depuis les
 * deux voisines) pour couvrir les 12 catégories réelles du pool.
 *
 * LIMITE ASSUMÉE : validé avec `node scripts/validate_palette.js` en
 * --pairs adjacent (légende, liste) mais PAS en --pairs all — le skill lui-
 * même indique qu'aucun ordre de 8 teintes ne passe ce mode au-delà de 3
 * séries, donc 12 sur un globe (où deux zones voisines peuvent être
 * n'importe quelle paire de catégories) ne peut pas y arriver non plus.
 * Mitigation : la couleur n'est JAMAIS le seul canal d'identité — une
 * légende texte est toujours affichée, et le clic sur une zone révèle
 * toujours le nom de la catégorie en texte.
 */
export const CATEGORY_COLORS: Record<string, string> = {
  "économique": "#2a78d6",
  "institutionnel": "#eb6834",
  "commerce": "#1baf7a",
  "démographie/migration": "#eda100",
  "géopolitique": "#e87ba4",
  "géologique/climatique": "#008300",
  "vulnérabilité": "#4a3aa7",
  "biologique": "#e34948",
  "écologique": "#009eb7",
  "technologique": "#a055b0",
  "psychologique": "#989400",
  "juridique": "#009c8d",
};

export const FALLBACK_CATEGORY_COLOR = "#777777";

export function categoryColor(category: string): string {
  return CATEGORY_COLORS[category] ?? FALLBACK_CATEGORY_COLOR;
}

function shade(hex: string, factor: number): string {
  const h = hex.replace("#", "");
  const [r, g, b] = [0, 2, 4].map(i => parseInt(h.slice(i, i + 2), 16));
  const clamp = (v: number) => Math.max(0, Math.min(255, Math.round(v)));
  return (
    "#" +
    [r, g, b]
      .map(v => clamp(v * factor).toString(16).padStart(2, "0"))
      .join("")
  );
}

// Thème clair (fond blanc, cohérent avec le reste de la démo) : l'océan et
// les zones non découvertes partagent EXACTEMENT la même teinte, pour que
// les pays non découverts restent invisibles (aucun contour) — seule la
// couleur change par rapport à un thème sombre, jamais la règle "invisible
// tant que non découvert".
export const ZONE_RENDER = {
  undiscovered: { fill: "#f4f6fa", stroke: null as string | null },
  encountered: { fill: "#5b6472", stroke: "#8b95a5" },
  oceanBackground: "#f4f6fa",
};

export function masteredFill(category: string): string {
  return categoryColor(category);
}
export function masteredStroke(category: string): string {
  return shade(categoryColor(category), 0.65);
}
