export type ZoneState = "undiscovered" | "encountered" | "mastered";

export interface Encounter {
  date: string;
  situation: string;
  explanation: string;
  source: string;
}

export interface MechanismEntry {
  id: string;
  category: string;
  label: string;
  state: ZoneState;
  cause_effect?: string; // résumé causal "Cause→Effet", toujours affiché avec le mécanisme
  encounters?: Encounter[];
}

export interface ZoneMapping {
  zoneId: string;
  countryIds: string[];
  category: string;
  centroid: [number, number]; // [lon, lat]
  totalWeight: number;
}

export interface GeoCountry {
  id: string;
  feature: GeoJSON.Feature;
  centroid: [number, number];
  weight: number;
}
