import {
  forwardRef,
  useEffect,
  useImperativeHandle,
  useMemo,
  useRef,
  useState,
} from "react";
import { Canvas, type ThreeEvent } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { geoContains } from "d3-geo";
import type * as THREE from "three";
import type { MechanismEntry, ZoneState } from "./types";
import { useZoneMapping } from "./useZoneMapping";
import { loadCountries, makeProjection, CANVAS_WIDTH, CANVAS_HEIGHT } from "./geo";
import { buildCountryToZone, drawMap, createMapCanvas, createTexture } from "./texture";
import { ZoneDetailPanel } from "./ZoneDetailPanel";

export interface MechanismGlobeHandle {
  setZoneState: (mechanismId: string, newState: ZoneState) => void;
  recomputeZones: (mechanismPool: MechanismEntry[]) => void;
}

export interface MechanismGlobeProps {
  mechanismPool: MechanismEntry[];
  onZoneClick?: (mechanism: MechanismEntry) => void;
  className?: string;
}

function GlobeMesh({
  texture,
  onSurfaceClick,
}: {
  texture: THREE.Texture;
  onSurfaceClick: (uv: { x: number; y: number }) => void;
}) {
  return (
    <mesh
      onClick={(e: ThreeEvent<MouseEvent>) => {
        e.stopPropagation();
        if (e.uv) onSurfaceClick({ x: e.uv.x, y: e.uv.y });
      }}
    >
      <sphereGeometry args={[1, 64, 64]} />
      <meshStandardMaterial map={texture} roughness={1} metalness={0} />
    </mesh>
  );
}

export const MechanismGlobe = forwardRef<MechanismGlobeHandle, MechanismGlobeProps>(
  function MechanismGlobe({ mechanismPool, onZoneClick, className }, ref) {
    const [mechanisms, setMechanisms] = useState<MechanismEntry[]>(mechanismPool);
    const lastPropPoolRef = useRef(mechanismPool);
    const [selected, setSelected] = useState<MechanismEntry | null>(null);

    // Le pool injecté par le parent est la source de vérité pour la
    // COMPOSITION (ajout/retrait/catégorie) ; l'état (setZoneState) reste
    // géré en interne via la ref pour ne pas dépendre d'un re-render parent.
    useEffect(() => {
      if (lastPropPoolRef.current !== mechanismPool) {
        lastPropPoolRef.current = mechanismPool;
        setMechanisms(mechanismPool);
      }
    }, [mechanismPool]);

    const { mapping, signature } = useZoneMapping(mechanisms);

    const countries = useMemo(() => loadCountries(), []);
    const projection = useMemo(() => makeProjection(), []);
    const countryToZone = useMemo(() => buildCountryToZone(mapping), [mapping]);
    const mechanismsById = useMemo(() => {
      const m = new Map<string, MechanismEntry>();
      mechanisms.forEach(mech => m.set(mech.id, mech));
      return m;
    }, [mechanisms]);

    const canvasRef = useRef<HTMLCanvasElement | null>(null);
    if (canvasRef.current === null) canvasRef.current = createMapCanvas();
    const textureRef = useRef<THREE.CanvasTexture | null>(null);
    if (textureRef.current === null) textureRef.current = createTexture(canvasRef.current);

    useEffect(() => {
      const ctx = canvasRef.current!.getContext("2d");
      if (!ctx) return;
      drawMap(ctx, projection, countries, countryToZone, mechanismsById);
      textureRef.current!.needsUpdate = true;
      // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [countryToZone, mechanismsById, signature]);

    useImperativeHandle(
      ref,
      () => ({
        setZoneState(mechanismId, newState) {
          setMechanisms(prev =>
            prev.map(m => (m.id === mechanismId ? { ...m, state: newState } : m))
          );
        },
        recomputeZones(newPool) {
          lastPropPoolRef.current = newPool;
          setMechanisms(newPool);
        },
      }),
      []
    );

    function handleSurfaceClick(uv: { x: number; y: number }) {
      const px = uv.x * CANVAS_WIDTH;
      // flipY par défaut sur CanvasTexture : v=0 correspond au bas du canvas.
      const py = (1 - uv.y) * CANVAS_HEIGHT;
      const lonLat = projection.invert?.([px, py]);
      if (!lonLat) return;
      const [lon, lat] = lonLat;

      const country = countries.find(c => geoContains(c.feature, [lon, lat]));
      const zone = country ? countryToZone.get(country.id) : undefined;
      const mech = zone ? mechanismsById.get(zone.zoneId) : undefined;
      if (!mech || mech.state === "undiscovered") return; // pas de spoil

      if (onZoneClick) onZoneClick(mech);
      else setSelected(mech);
    }

    return (
      <div className={className} style={{ width: "100%", height: "100%", minHeight: 360 }}>
        <Canvas camera={{ position: [0, 0, 2.6], fov: 45 }}>
          <ambientLight intensity={0.7} />
          <directionalLight position={[3, 2, 4]} intensity={0.8} />
          <GlobeMesh texture={textureRef.current!} onSurfaceClick={handleSurfaceClick} />
          <OrbitControls
            enablePan={false}
            enableZoom={true}
            minDistance={1.6}
            maxDistance={4}
            enableDamping
            dampingFactor={0.1}
            rotateSpeed={0.5}
          />
        </Canvas>
        {selected && <ZoneDetailPanel mechanism={selected} onClose={() => setSelected(null)} />}
      </div>
    );
  }
);
