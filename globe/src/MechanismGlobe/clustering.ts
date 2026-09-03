import type { GeoCountry, MechanismEntry, ZoneMapping } from "./types";

/**
 * Découpage géographique dynamique en N zones (N = taille du pool de
 * mécanismes), recalculé entièrement à chaque changement du pool.
 *
 * Algorithme : k-means sphérique pondéré par l'aire réelle des pays
 * (Lloyd sur des vecteurs 3D unitaires, pas sur lon/lat bruts — évite les
 * artefacts de l'antiméridien et des pôles), suivi d'une passe de
 * rééquilibrage gloutonne qui transfère les pays "frontière" des clusters
 * en surcharge vers les clusters sous-chargés, pour éviter qu'une zone
 * minuscule (ex: Europe dense) coexiste avec une zone énorme (ex: Sibérie/
 * Pacifique clairsemé). Déterministe : graine fixe + ordre d'entrée stable
 * => mêmes données en entrée = mêmes zones en sortie, à chaque relance.
 */

type Vec3 = [number, number, number];

const SEED = 1337;

/** PRNG déterministe (mulberry32) — jamais Math.random() ici. */
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

function lonLatToVec3(lon: number, lat: number): Vec3 {
  const lonR = (lon * Math.PI) / 180;
  const latR = (lat * Math.PI) / 180;
  return [
    Math.cos(latR) * Math.cos(lonR),
    Math.cos(latR) * Math.sin(lonR),
    Math.sin(latR),
  ];
}

function vec3ToLonLat(v: Vec3): [number, number] {
  const [x, y, z] = v;
  const lat = (Math.asin(Math.max(-1, Math.min(1, z))) * 180) / Math.PI;
  const lon = (Math.atan2(y, x) * 180) / Math.PI;
  return [lon, lat];
}

function normalize(v: Vec3): Vec3 {
  const n = Math.hypot(v[0], v[1], v[2]) || 1;
  return [v[0] / n, v[1] / n, v[2] / n];
}

function dot(a: Vec3, b: Vec3): number {
  return a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
}

interface Point {
  id: string;
  vec: Vec3;
  weight: number;
}

/** Sélection déterministe des centroïdes initiaux (k-means++ pondéré, PRNG seedé). */
function seedCentroids(points: Point[], k: number): Vec3[] {
  const rng = mulberry32(SEED);
  const centroids: Vec3[] = [];
  const first = points[Math.floor(rng() * points.length)];
  centroids.push(first.vec);

  while (centroids.length < k) {
    const dists = points.map(p => {
      // k-means++ : pondérer par la distance au centroïde le PLUS PROCHE
      // (pas le plus loin) déjà choisi, pour répartir les graines initiales.
      const dMin = Math.min(
        ...centroids.map(c => 1 - dot(c, p.vec)) // distance angulaire ~ 1-cos
      );
      return dMin * dMin * p.weight;
    });
    const total = dists.reduce((a, b) => a + b, 0);
    if (total <= 0) {
      // fallback : tous les points déjà couverts par un centroïde identique
      centroids.push(points[centroids.length % points.length].vec);
      continue;
    }
    let r = rng() * total;
    let idx = 0;
    for (; idx < dists.length; idx++) {
      r -= dists[idx];
      if (r <= 0) break;
    }
    centroids.push(points[Math.min(idx, points.length - 1)].vec);
  }
  return centroids;
}

function weightedKMeansSphere(points: Point[], k: number, maxIter = 50): number[] {
  let centroids = seedCentroids(points, k);
  let assignment = new Array(points.length).fill(0);

  for (let iter = 0; iter < maxIter; iter++) {
    let changed = false;
    const newAssignment = points.map((p, i) => {
      let best = 0;
      let bestScore = -Infinity;
      for (let c = 0; c < centroids.length; c++) {
        const score = dot(centroids[c], p.vec);
        if (score > bestScore) {
          bestScore = score;
          best = c;
        }
      }
      if (best !== assignment[i]) changed = true;
      return best;
    });
    assignment = newAssignment;

    const sums: Vec3[] = Array.from({ length: k }, () => [0, 0, 0]);
    for (let i = 0; i < points.length; i++) {
      const c = assignment[i];
      const w = points[i].weight;
      sums[c][0] += points[i].vec[0] * w;
      sums[c][1] += points[i].vec[1] * w;
      sums[c][2] += points[i].vec[2] * w;
    }
    centroids = sums.map((s, c) => {
      const anyAssigned = assignment.includes(c);
      return anyAssigned ? normalize(s) : centroids[c];
    });

    // Filet de sécurité anti-cluster-mort : un centroïde qui n'a jamais gagné
    // le moindre point reste bloqué à sa position de départ pour toujours
    // (aucun concurrent ne le laissera jamais gagner ensuite). On le
    // ré-ensemence sur le point actuellement le plus mal desservi par son
    // propre cluster (le plus loin de son centroïde), qui repart avec lui.
    const presentClusters = new Set(assignment);
    for (let c = 0; c < k; c++) {
      if (presentClusters.has(c)) continue;
      let worstIdx = -1;
      let worstDist = -Infinity;
      for (let i = 0; i < points.length; i++) {
        const owner = assignment[i];
        if (!presentClusters.has(owner)) continue; // ne pas vider un cluster déjà fragile
        const clusterSize = points.filter((_, j) => assignment[j] === owner).length;
        if (clusterSize <= 1) continue; // ne jamais vider un cluster à un seul pays
        const d = 1 - dot(centroids[owner], points[i].vec);
        if (d > worstDist) {
          worstDist = d;
          worstIdx = i;
        }
      }
      if (worstIdx >= 0) {
        assignment[worstIdx] = c;
        centroids[c] = points[worstIdx].vec;
        presentClusters.add(c);
        changed = true;
      }
    }

    if (!changed && iter > 0) break;
  }

  return assignment;
}

/**
 * Rééquilibrage glouton par aire : transfère les pays frontière des clusters
 * en surcharge vers les clusters sous-chargés.
 *
 * Un pays-continent seul (Russie, Canada...) peut dépasser la cible à lui
 * seul et ne rien pouvoir céder sans laisser un cluster vide — ce plancher
 * est physique (granularité "pays entier"), pas un bug. Le point important :
 * quand le cluster le PLUS chargé est un tel singleton, il ne faut pas
 * abandonner tout le rééquilibrage pour autant — on continue avec le
 * prochain cluster surchargé qui peut réellement donner un pays.
 */
function rebalance(points: Point[], assignment: number[], k: number, maxPasses = 300): number[] {
  const totalWeight = points.reduce((s, p) => s + p.weight, 0);
  const target = totalWeight / k;
  const out = [...assignment];

  const clusterStats = (a: number[]) => {
    const w = new Array(k).fill(0);
    const n = new Array(k).fill(0);
    a.forEach((c, i) => {
      w[c] += points[i].weight;
      n[c] += 1;
    });
    return { w, n };
  };
  const centroidOf = (a: number[], c: number): Vec3 => {
    let sum: Vec3 = [0, 0, 0];
    let wsum = 0;
    a.forEach((cc, i) => {
      if (cc === c) {
        sum = [
          sum[0] + points[i].vec[0] * points[i].weight,
          sum[1] + points[i].vec[1] * points[i].weight,
          sum[2] + points[i].vec[2] * points[i].weight,
        ];
        wsum += points[i].weight;
      }
    });
    return wsum > 0 ? normalize(sum) : [0, 0, 0];
  };

  for (let pass = 0; pass < maxPasses; pass++) {
    const { w: weights, n: counts } = clusterStats(out);

    // Cluster le plus chargé PARMI CEUX QUI PEUVENT DONNER (>1 pays) — un
    // singleton géant ne bloque plus les passes suivantes.
    let overloaded = -1;
    let overloadedW = -Infinity;
    for (let c = 0; c < k; c++) {
      if (counts[c] > 1 && weights[c] > overloadedW) {
        overloadedW = weights[c];
        overloaded = c;
      }
    }
    if (overloaded === -1) break; // plus aucun cluster ne peut céder de pays

    // Cluster le plus léger (n'importe lequel, y compris un singleton).
    let underloaded = -1;
    let underloadedW = Infinity;
    for (let c = 0; c < k; c++) {
      if (c === overloaded) continue;
      if (weights[c] < underloadedW) {
        underloadedW = weights[c];
        underloaded = c;
      }
    }
    if (underloaded === -1) break;

    // Rien à gagner : le donneur n'est plus vraiment en surcharge, ou le
    // receveur n'est plus vraiment sous-chargé.
    if (overloadedW <= target * 1.15 && underloadedW >= target * 0.85) break;

    const underCentroid = centroidOf(out, underloaded);
    const candidates = points
      .map((p, i) => ({ i, p }))
      .filter(({ i }) => out[i] === overloaded);

    let bestIdx = -1;
    let bestScore = -Infinity;
    for (const { i, p } of candidates) {
      const score = dot(p.vec, underCentroid);
      if (score > bestScore) {
        bestScore = score;
        bestIdx = i;
      }
    }
    if (bestIdx === -1) break;
    out[bestIdx] = underloaded;
  }

  return out;
}

export interface ClusterResult {
  zoneId: string;
  countryIds: string[];
  centroid: [number, number];
  totalWeight: number;
}

/** Étape 1 : découpe les pays en k clusters géographiques équilibrés (sans les nommer). */
export function clusterCountries(countries: GeoCountry[], k: number): ClusterResult[] {
  if (k <= 0 || countries.length === 0) return [];
  const kEff = Math.min(k, countries.length);

  const points: Point[] = countries.map(c => ({
    id: c.id,
    vec: lonLatToVec3(c.centroid[0], c.centroid[1]),
    weight: c.weight,
  }));

  let assignment = weightedKMeansSphere(points, kEff);
  assignment = rebalance(points, assignment, kEff);

  const clusters: ClusterResult[] = Array.from({ length: kEff }, (_, c) => {
    const members = countries.filter((_, i) => assignment[i] === c);
    const sum = members.reduce(
      (acc, m) => {
        const v = lonLatToVec3(m.centroid[0], m.centroid[1]);
        return [acc[0] + v[0] * m.weight, acc[1] + v[1] * m.weight, acc[2] + v[2] * m.weight] as Vec3;
      },
      [0, 0, 0] as Vec3
    );
    const centroidVec = normalize(sum);
    const [lon, lat] = vec3ToLonLat(centroidVec);
    return {
      zoneId: `zone_${c}`,
      countryIds: members.map(m => m.id),
      centroid: [lon, lat] as [number, number],
      totalWeight: members.reduce((s, m) => s + m.weight, 0),
    };
  }).filter(c => c.countryIds.length > 0);

  return clusters;
}

/**
 * Étape 2 : appariement déterministe zones <-> mécanismes. Zones triées
 * nord->sud puis ouest->est ; mécanismes triés (catégorie, id) — même
 * ordre à chaque appel => même mapping tant que le pool ne change pas.
 */
export function assignZonesToMechanisms(
  clusters: ClusterResult[],
  mechanismPool: MechanismEntry[]
): ZoneMapping[] {
  const orderedClusters = [...clusters].sort((a, b) => {
    const latDiff = b.centroid[1] - a.centroid[1]; // nord -> sud
    if (Math.abs(latDiff) > 1e-9) return latDiff;
    return a.centroid[0] - b.centroid[0]; // ouest -> est
  });
  const orderedMechanisms = [...mechanismPool].sort((a, b) => {
    if (a.category !== b.category) return a.category < b.category ? -1 : 1;
    return a.id < b.id ? -1 : a.id > b.id ? 1 : 0;
  });

  const n = Math.min(orderedClusters.length, orderedMechanisms.length);
  const mapping: ZoneMapping[] = [];
  for (let i = 0; i < n; i++) {
    const cluster = orderedClusters[i];
    const mech = orderedMechanisms[i];
    mapping.push({
      zoneId: mech.id,
      countryIds: cluster.countryIds,
      category: mech.category,
      centroid: cluster.centroid,
      totalWeight: cluster.totalWeight,
    });
  }
  return mapping;
}

/** Signature stable du pool (composition, pas état) — clé de mémoïsation du recalcul. */
export function poolSignature(mechanismPool: MechanismEntry[]): string {
  return mechanismPool
    .map(m => `${m.id}:${m.category}`)
    .sort()
    .join("|");
}
