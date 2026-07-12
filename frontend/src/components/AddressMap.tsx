"use client";

import "leaflet/dist/leaflet.css";

import L from "leaflet";
import { useEffect, useRef, useState } from "react";
import { MapContainer, Marker, TileLayer, useMap, useMapEvents } from "react-leaflet";

export interface PickedLocation {
  address: string;
  latitude: number;
  longitude: number;
}

interface NominatimResult {
  lat: string;
  lon: string;
  display_name: string;
}

// A gold teardrop pin as an HTML div-icon (avoids Leaflet's default-icon
// bundling problem entirely).
const pinIcon = L.divIcon({
  className: "",
  html: `<svg width="34" height="34" viewBox="0 0 24 24" fill="#b8862f" stroke="#1c1713" stroke-width="1">
    <path d="M12 2C8.1 2 5 5.1 5 9c0 5.2 7 13 7 13s7-7.8 7-13c0-3.9-3.1-7-7-7z"/>
    <circle cx="12" cy="9" r="2.5" fill="#fff"/></svg>`,
  iconSize: [34, 34],
  iconAnchor: [17, 34],
});

/** Recenters the map whenever the chosen position changes. */
function Recenter({ pos }: { pos: [number, number] }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo(pos, Math.max(map.getZoom(), 15));
  }, [pos, map]);
  return null;
}

/** Lets the user click anywhere on the map to drop the pin there. */
function ClickToPlace({ onPick }: { onPick: (lat: number, lng: number) => void }) {
  useMapEvents({
    click(e) {
      onPick(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
}

async function reverseGeocode(lat: number, lng: number): Promise<string> {
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`,
    );
    const data = await res.json();
    return data.display_name ?? `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
  } catch {
    return `${lat.toFixed(5)}, ${lng.toFixed(5)}`;
  }
}

export default function AddressMap({
  onChange,
}: {
  onChange: (loc: PickedLocation) => void;
}) {
  // Default view: a neutral world-ish center until the user searches.
  const [pos, setPos] = useState<[number, number]>([30.3753, 69.3451]);
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<NominatimResult[]>([]);
  const [selected, setSelected] = useState("");
  const [searching, setSearching] = useState(false);
  const debounce = useRef<ReturnType<typeof setTimeout>>();

  // Debounced address search via OpenStreetMap Nominatim.
  useEffect(() => {
    if (query.trim().length < 3 || query === selected) {
      setResults([]);
      return;
    }
    clearTimeout(debounce.current);
    setSearching(true);
    debounce.current = setTimeout(async () => {
      try {
        const res = await fetch(
          `https://nominatim.openstreetmap.org/search?format=json&limit=5&q=${encodeURIComponent(query)}`,
        );
        setResults(await res.json());
      } catch {
        setResults([]);
      } finally {
        setSearching(false);
      }
    }, 450);
    return () => clearTimeout(debounce.current);
  }, [query, selected]);

  const commit = (lat: number, lng: number, address: string) => {
    setPos([lat, lng]);
    setSelected(address);
    setQuery(address);
    setResults([]);
    onChange({ address, latitude: lat, longitude: lng });
  };

  const chooseResult = (r: NominatimResult) =>
    commit(parseFloat(r.lat), parseFloat(r.lon), r.display_name);

  const placeByCoords = async (lat: number, lng: number) => {
    const address = await reverseGeocode(lat, lng);
    commit(lat, lng, address);
  };

  return (
    <div>
      {/* Search box */}
      <div className="relative">
        <input
          type="text"
          value={query}
          onChange={(e) => {
            setQuery(e.target.value);
            setSelected("");
          }}
          placeholder="Search your address, or drop a pin on the map"
          aria-label="Search delivery address"
          className="w-full rounded-xl border border-cream-300 bg-cream-50 px-4 py-3 text-espresso-900 placeholder:text-espresso-400 focus:border-gold-500 focus:outline-none focus:ring-2 focus:ring-gold-500/30"
        />
        {(results.length > 0 || searching) && (
          <ul className="absolute z-[1000] mt-1 max-h-60 w-full overflow-auto rounded-xl border border-cream-300 bg-cream-50 shadow-card">
            {searching && (
              <li className="px-4 py-2 text-sm text-espresso-400">Searching…</li>
            )}
            {results.map((r, i) => (
              <li key={i}>
                <button
                  type="button"
                  onClick={() => chooseResult(r)}
                  className="block w-full px-4 py-2 text-left text-sm text-espresso-800 hover:bg-cream-200"
                >
                  {r.display_name}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      {/* Map */}
      <div className="mt-3 overflow-hidden rounded-xl border border-cream-300">
        <MapContainer
          center={pos}
          zoom={5}
          scrollWheelZoom={false}
          style={{ height: 280, width: "100%" }}
        >
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Marker
            position={pos}
            icon={pinIcon}
            draggable
            eventHandlers={{
              dragend: (e) => {
                const m = e.target.getLatLng();
                placeByCoords(m.lat, m.lng);
              },
            }}
          />
          <ClickToPlace onPick={placeByCoords} />
          <Recenter pos={pos} />
        </MapContainer>
      </div>

      {selected && (
        <p className="text-espresso-700 mt-2 rounded-lg bg-cream-200/70 px-3 py-2 text-sm">
          📍 {selected}
        </p>
      )}
    </div>
  );
}
