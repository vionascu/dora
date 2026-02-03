import 'maplibre-gl/dist/maplibre-gl.css';
import { useEffect, useRef } from 'react';
import { View } from 'react-native';

const MAP_CENTER = [25.43, 45.4];
const MAP_ZOOM = 12;

const getMapStyle = () => ({
  version: 8,
  sources: {
    osm: {
      type: 'raster',
      tiles: ['https://tile.openstreetmap.org/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: '© OpenStreetMap contributors',
    },
    hiking: {
      type: 'raster',
      tiles: ['https://tile.waymarkedtrails.org/hiking/{z}/{x}/{y}.png'],
      tileSize: 256,
      attribution: '© waymarkedtrails.org, OpenStreetMap contributors',
    },
  },
  layers: [
    {
      id: 'osm',
      type: 'raster',
      source: 'osm',
    },
    {
      id: 'hiking-trails',
      type: 'raster',
      source: 'hiking',
      paint: {
        'raster-opacity': 0.85,
      },
    },
  ],
});

export default function WebMap({ style, onMapPress, reports, reportMode }) {
  const containerRef = useRef(null);
  const mapRef = useRef(null);
  const maplibreRef = useRef(null);
  const markersRef = useRef([]);
  const onMapPressRef = useRef(onMapPress);

  useEffect(() => {
    onMapPressRef.current = onMapPress;
  }, [onMapPress]);

  useEffect(() => {
    const setupMap = async () => {
      const module = await import('maplibre-gl');
      const maplibre = module.default || module;
      maplibre.accessToken = '';
      maplibreRef.current = maplibre;

      if (!containerRef.current) {
        return;
      }

      const map = new maplibre.Map({
        container: containerRef.current,
        style: getMapStyle(),
        center: MAP_CENTER,
        zoom: MAP_ZOOM,
      });
      mapRef.current = map;

      map.on('load', () => {
        map.resize();
      });

      map.on('click', (event) => {
        const handler = onMapPressRef.current;
        if (!handler) return;
        handler({ coordinates: [event.lngLat.lng, event.lngLat.lat] });
      });
    };

    setupMap();

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!mapRef.current) {
      return;
    }

    const canvas = mapRef.current.getCanvas();
    canvas.style.cursor = reportMode ? 'crosshair' : '';
  }, [reportMode]);

  useEffect(() => {
    if (!mapRef.current || !maplibreRef.current) {
      return;
    }

    markersRef.current.forEach((marker) => marker.remove());
    const maplibre = maplibreRef.current;
    markersRef.current = reports.map((report) => {
      const markerEl = document.createElement('div');
      markerEl.style.width = '24px';
      markerEl.style.height = '24px';
      markerEl.style.borderRadius = '12px';
      markerEl.style.backgroundColor = '#f2b155';
      markerEl.style.border = '2px solid #1b1b1b';
      markerEl.style.display = 'flex';
      markerEl.style.alignItems = 'center';
      markerEl.style.justifyContent = 'center';
      markerEl.style.color = '#1b1b1b';
      markerEl.style.fontSize = '12px';
      markerEl.style.fontWeight = '700';
      markerEl.textContent = report.label.slice(0, 1).toUpperCase();

      const marker = new maplibre.Marker({ element: markerEl })
        .setLngLat(report.coordinate)
        .addTo(mapRef.current);

      return marker;
    });
  }, [reports]);

  return <View ref={containerRef} style={style} />;
}
