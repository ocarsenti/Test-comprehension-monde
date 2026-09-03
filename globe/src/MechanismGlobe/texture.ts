import { geoGraticule, geoPath, type GeoProjection } from "d3-geo";
import * as THREE from "three";
import type { GeoCountry, ZoneMapping, MechanismEntry } from "./types";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "./geo";
import { ZONE_RENDER, masteredFill, masteredStroke, GRATICULE_COLOR, EQUATOR_COLOR } from "./colors";

const EQUATOR: GeoJSON.LineString = {
  type: "LineString",
  coordinates: Array.from({ length: 73 }, (_, i) => [i * 5 - 180, 0]),
};

function drawGraticule(ctx: CanvasRenderingContext2D, projection: GeoProjection) {
  const path = geoPath(projection, ctx);
  const graticule = geoGraticule().step([20, 20])();

  ctx.beginPath();
  path(graticule);
  ctx.lineWidth = 1;
  ctx.strokeStyle = GRATICULE_COLOR;
  ctx.stroke();

  // équateur en plus gras, pour repérer tout de suite qu'il s'agit de la Terre.
  ctx.beginPath();
  path(EQUATOR);
  ctx.lineWidth = 2.5;
  ctx.strokeStyle = EQUATOR_COLOR;
  ctx.stroke();
}

export function buildCountryToZone(mapping: ZoneMapping[]): Map<string, ZoneMapping> {
  const m = new Map<string, ZoneMapping>();
  for (const zone of mapping) {
    for (const countryId of zone.countryIds) {
      m.set(countryId, zone);
    }
  }
  return m;
}

export function drawMap(
  ctx: CanvasRenderingContext2D,
  projection: GeoProjection,
  countries: GeoCountry[],
  countryToZone: Map<string, ZoneMapping>,
  mechanismsById: Map<string, MechanismEntry>
) {
  const path = geoPath(projection, ctx);

  ctx.fillStyle = ZONE_RENDER.oceanBackground;
  ctx.fillRect(0, 0, CANVAS_WIDTH, CANVAS_HEIGHT);

  // Quadrillage lat/long dessiné sur le fond AVANT les pays : une zone non
  // découverte ne reçoit ensuite aucun tracé par-dessus (voir plus bas), donc
  // le quadrillage continue de la traverser sans interruption — impossible
  // d'en deviner le contour, tout en identifiant tout de suite le globe
  // comme la Terre dès le premier chargement (0 mécanisme rencontré).
  drawGraticule(ctx, projection);

  for (const country of countries) {
    const zone = countryToZone.get(country.id);
    const mech = zone ? mechanismsById.get(zone.zoneId) : undefined;
    const state = mech?.state ?? "undiscovered";

    if (state === "undiscovered") continue; // rien à dessiner : se fond dans le fond + grille.

    ctx.beginPath();
    path(country.feature);

    if (state === "mastered" && mech) {
      ctx.fillStyle = masteredFill(mech.category);
      ctx.fill();
      ctx.lineWidth = 1;
      ctx.strokeStyle = masteredStroke(mech.category);
      ctx.stroke();
    } else {
      ctx.fillStyle = ZONE_RENDER.encountered.fill;
      ctx.fill();
      ctx.lineWidth = 0.6;
      ctx.strokeStyle = ZONE_RENDER.encountered.stroke!;
      ctx.stroke();
    }
  }
}

export function createMapCanvas(): HTMLCanvasElement {
  const canvas = document.createElement("canvas");
  canvas.width = CANVAS_WIDTH;
  canvas.height = CANVAS_HEIGHT;
  return canvas;
}

export function createTexture(canvas: HTMLCanvasElement): THREE.CanvasTexture {
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace;
  texture.minFilter = THREE.LinearFilter;
  texture.magFilter = THREE.LinearFilter;
  return texture;
}
