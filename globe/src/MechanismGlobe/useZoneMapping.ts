import { useMemo } from "react";
import { loadCountries } from "./geo";
import { clusterCountries, assignZonesToMechanisms, poolSignature } from "./clustering";
import type { MechanismEntry, ZoneMapping } from "./types";

/**
 * Mémoïse le découpage géographique + l'appariement zone<->mécanisme sur la
 * SIGNATURE de composition du pool (id+catégorie), jamais sur les états —
 * changer l'état d'un mécanisme ne redéclenche donc jamais le clustering,
 * seul un ajout/retrait de mécanisme (ou changement de catégorie) le fait.
 */
export function useZoneMapping(mechanismPool: MechanismEntry[]): {
  mapping: ZoneMapping[];
  signature: string;
} {
  const signature = poolSignature(mechanismPool);

  const mapping = useMemo(() => {
    const countries = loadCountries();
    const clusters = clusterCountries(countries, mechanismPool.length);
    return assignZonesToMechanisms(clusters, mechanismPool);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [signature]);

  return { mapping, signature };
}
