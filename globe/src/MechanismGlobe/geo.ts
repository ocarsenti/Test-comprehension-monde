import { geoCentroid, geoArea, geoEquirectangular, type GeoProjection } from "d3-geo";
import { feature } from "topojson-client";
import worldTopo from "world-atlas/countries-110m.json";
import type { GeoCountry } from "./types";

export const CANVAS_WIDTH = 2048;
export const CANVAS_HEIGHT = 1024;

let cachedCountries: GeoCountry[] | null = null;

/** Pays du monde (résolution 110m), avec centroïde et aire (poids de clustering). */
export function loadCountries(): GeoCountry[] {
  if (cachedCountries) return cachedCountries;

  const topo = worldTopo as any;
  const collection = feature(
    topo,
    topo.objects.countries
  ) as unknown as GeoJSON.FeatureCollection;

  const countries: GeoCountry[] = [];
  for (const f of collection.features) {
    const centroid = geoCentroid(f);
    const weight = geoArea(f);
    // certaines géométries dégénérées (îles minuscules à 110m) donnent un
    // centroïde NaN ou une aire nulle — on les exclut du clustering plutôt
    // que de laisser un pays sans zone ou un poids invalide.
    if (!Number.isFinite(centroid[0]) || !Number.isFinite(centroid[1]) || !(weight > 0)) {
      continue;
    }
    countries.push({
      id: String((f as any).id ?? f.properties?.name ?? Math.random()),
      feature: f,
      centroid: centroid as [number, number],
      weight,
    });
  }

  cachedCountries = countries;
  return countries;
}

/** Projection équirectangulaire partagée par le dessin du canvas et l'inversion clic->pays. */
export function makeProjection(width = CANVAS_WIDTH, height = CANVAS_HEIGHT): GeoProjection {
  return geoEquirectangular()
    .scale(width / (2 * Math.PI))
    .translate([width / 2, height / 2]);
}
