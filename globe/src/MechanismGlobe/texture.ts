import { geoPath, type GeoProjection } from "d3-geo";
import * as THREE from "three";
import type { GeoCountry, ZoneMapping, MechanismEntry } from "./types";
import { CANVAS_WIDTH, CANVAS_HEIGHT } from "./geo";
import { ZONE_RENDER, masteredFill, masteredStroke } from "./colors";

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

  for (const country of countries) {
    const zone = countryToZone.get(country.id);
    const mech = zone ? mechanismsById.get(zone.zoneId) : undefined;
    const state = mech?.state ?? "undiscovered";

    ctx.beginPath();
    path(country.feature);

    if (state === "mastered" && mech) {
      ctx.fillStyle = masteredFill(mech.category);
      ctx.fill();
      ctx.lineWidth = 1;
      ctx.strokeStyle = masteredStroke(mech.category);
      ctx.stroke();
    } else if (state === "encountered") {
      ctx.fillStyle = ZONE_RENDER.encountered.fill;
      ctx.fill();
      ctx.lineWidth = 0.6;
      ctx.strokeStyle = ZONE_RENDER.encountered.stroke!;
      ctx.stroke();
    } else {
      ctx.fillStyle = ZONE_RENDER.undiscovered.fill;
      ctx.fill();
      // pas de contour pour les zones non découvertes — se fond dans le fond.
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
