import { useEffect, useMemo, useState } from 'react';
import { Asset } from 'expo-asset';
import { StatusBar } from 'expo-status-bar';
import * as FileSystem from 'expo-file-system';
import * as Location from 'expo-location';
import {
  ActivityIndicator,
  Pressable,
  Platform,
  SafeAreaView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import mbtilesAsset from './mbtiles';
import WebMap from './WebMap';

const MapLibreGL =
  Platform.OS === 'web'
    ? null
    : require('@maplibre/maplibre-react-native').default ||
      require('@maplibre/maplibre-react-native');

const REPORT_TYPES = [
  { key: 'bear', label: '🐻 Bear' },
  { key: 'fallen-tree', label: '🌲 Fallen tree' },
  { key: 'grohotis', label: '🪨 Scree' },
  { key: 'cabana-full', label: '🏔️ Hut full' },
];

export default function App() {
  const isWeb = Platform.OS === 'web';
  const [mbtilesPath, setMbtilesPath] = useState(null);
  const [locationDenied, setLocationDenied] = useState(false);
  const [reportMode, setReportMode] = useState(false);
  const [reportType, setReportType] = useState(null);
  const [reports, setReports] = useState([]);
  const [reportHint, setReportHint] = useState('');

  useEffect(() => {
    let isMounted = true;

    const prepareTiles = async () => {
      if (isWeb || !mbtilesAsset) {
        return;
      }

      const asset = Asset.fromModule(mbtilesAsset);
      await asset.downloadAsync();

      const targetPath = `${FileSystem.documentDirectory}bucegi.mbtiles`;
      const targetInfo = await FileSystem.getInfoAsync(targetPath);

      if (!targetInfo.exists) {
        if (!asset.localUri) {
          throw new Error('Bucegi MBTiles asset is missing a local URI.');
        }
        await FileSystem.copyAsync({ from: asset.localUri, to: targetPath });
      }

      if (isMounted) {
        setMbtilesPath(targetPath);
      }
    };

    prepareTiles();

    return () => {
      isMounted = false;
    };
  }, [isWeb]);

  useEffect(() => {
    let isMounted = true;

    const requestLocation = async () => {
      if (isWeb) {
        return;
      }

      const { status } = await Location.requestForegroundPermissionsAsync();
      if (isMounted) {
        setLocationDenied(status !== 'granted');
      }
    };

    requestLocation();

    return () => {
      isMounted = false;
    };
  }, [isWeb]);

  const mapStyle = useMemo(() => {
    if (!mbtilesPath) {
      return null;
    }

    const normalizedPath = mbtilesPath.startsWith('file://')
      ? mbtilesPath.replace('file://', '')
      : mbtilesPath;

    return {
      version: 8,
      sources: {
        bucegi: {
          type: 'vector',
          tiles: [`mbtiles://${normalizedPath}`],
          minzoom: 10,
          maxzoom: 16,
        },
      },
      layers: [
        {
          id: 'background',
          type: 'background',
          paint: {
            'background-color': '#142624',
          },
        },
        {
          id: 'bucegi-trails',
          type: 'line',
          source: 'bucegi',
          'source-layer': 'bucegi',
          filter: [
            'any',
            ['==', ['get', 'highway'], 'path'],
            ['==', ['get', 'highway'], 'footway'],
            ['==', ['get', 'highway'], 'track'],
            ['==', ['get', 'marked_trail'], 'yes'],
            ['==', ['get', 'route'], 'hiking'],
            ['==', ['get', 'mtb'], 'yes'],
          ],
          paint: {
            'line-color': '#f2b155',
            'line-width': [
              'interpolate',
              ['linear'],
              ['zoom'],
              10,
              0.8,
              12,
              1.6,
              14,
              2.4,
              16,
              3.4,
            ],
            'line-opacity': 0.9,
          },
          layout: {
            'line-join': 'round',
            'line-cap': 'round',
          },
        },
      ],
    };
  }, [mbtilesPath]);

  const handleReportPress = () => {
    setReportHint('');
    setReportMode(true);
    setReportType(null);
  };

  const handleMapPress = (event) => {
    if (!reportMode || !reportType) {
      return;
    }

    const coordinates =
      event?.geometry?.coordinates || event?.coordinates || null;
    if (!coordinates || coordinates.length < 2) {
      return;
    }

    const typeLabel =
      REPORT_TYPES.find((item) => item.key === reportType)?.label || reportType;
    const report = {
      id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
      type: reportType,
      label: typeLabel,
      coordinate: coordinates,
    };

    setReports((prev) => [...prev, report]);
    setReportMode(false);
    setReportType(null);
    setReportHint(`✅ Report added: ${typeLabel}.`);
  };

  return (
    <SafeAreaView style={styles.container} testID="app-root">
      <View style={styles.header}>
        <Text style={styles.title} testID="app-title">
          Trailwaze
        </Text>
        <Text style={styles.subtitle}>Offline-first hiking reports</Text>
      </View>

      <View style={styles.mapPlaceholder} testID="map-placeholder">
        {isWeb ? (
          <WebMap
            style={styles.map}
            onMapPress={handleMapPress}
            reports={reports}
            reportMode={reportMode && !!reportType}
          />
        ) : mapStyle && MapLibreGL ? (
          <MapLibreGL.MapView
            style={styles.map}
            mapStyle={mapStyle}
            compassEnabled
            logoEnabled={false}
            attributionEnabled={false}
            onPress={handleMapPress}
          >
            <MapLibreGL.Camera
              zoomLevel={12}
              centerCoordinate={[25.43, 45.4]}
            />
            <MapLibreGL.UserLocation visible />
            {reports.map((report) => (
              <MapLibreGL.PointAnnotation
                key={report.id}
                id={report.id}
                coordinate={report.coordinate}
              >
                <View style={styles.reportPin}>
                  <Text style={styles.reportPinText}>
                    {report.label.slice(0, 1).toUpperCase()}
                  </Text>
                </View>
              </MapLibreGL.PointAnnotation>
            ))}
          </MapLibreGL.MapView>
        ) : (
          <View style={styles.mapLoading}>
            <ActivityIndicator color="#f2b155" />
            <Text style={styles.mapText}>Preparing offline map...</Text>
            <Text style={styles.mapSubtext}>Copying MBTiles to device</Text>
          </View>
        )}
      </View>

      {locationDenied ? (
        <Text style={styles.permissionHint}>
          Location permission is needed to show your GPS dot.
        </Text>
      ) : null}

      <View style={styles.actions}>
        {reportMode ? (
          <View style={styles.reportPanel}>
            <Text style={styles.reportPanelTitle}>📋 Choose report type</Text>
            <View style={styles.reportOptions}>
              {REPORT_TYPES.map((item) => (
                <Pressable
                  key={item.key}
                  onPress={() => setReportType(item.key)}
                  style={[
                    styles.reportOption,
                    reportType === item.key && styles.reportOptionActive,
                  ]}
                >
                  <Text
                    style={[
                      styles.reportOptionText,
                      reportType === item.key && styles.reportOptionTextActive,
                    ]}
                  >
                    {item.label}
                  </Text>
                </Pressable>
              ))}
            </View>
            <Text style={styles.reportInstruction}>
              {reportType
                ? '👆 Tap map to place pin'
                : '✓ Choose type then tap map'}
            </Text>
            <Pressable
              onPress={() => {
                setReportMode(false);
                setReportType(null);
              }}
              style={styles.reportCancel}
            >
              <Text style={styles.reportCancelText}>✕ Cancel</Text>
            </Pressable>
          </View>
        ) : (
          <Pressable
            style={styles.reportButton}
            onPress={handleReportPress}
            testID="report-button"
          >
            <Text style={styles.reportText}>📍 Report</Text>
          </Pressable>
        )}
        {reportHint ? (
          <Text style={styles.reportHint}>{reportHint}</Text>
        ) : null}
        <Text style={styles.hint}>
          🐻 Bear | 🌲 Fallen tree | 🪨 Scree | 🏔️ Hut full
        </Text>
      </View>
      <StatusBar style="auto" />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0f1c1a',
  },
  header: {
    paddingHorizontal: 20,
    paddingTop: 12,
    paddingBottom: 8,
  },
  title: {
    color: '#f5f3e9',
    fontSize: 28,
    fontWeight: '700',
  },
  subtitle: {
    color: '#c6d4cf',
    marginTop: 4,
  },
  mapPlaceholder: {
    flex: 1,
    marginHorizontal: 20,
    marginTop: 12,
    marginBottom: 16,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#355e57',
    backgroundColor: '#142624',
    overflow: 'hidden',
  },
  map: {
    flex: 1,
  },
  mapLoading: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  mapText: {
    color: '#f5f3e9',
    fontSize: 16,
    fontWeight: '600',
  },
  mapSubtext: {
    color: '#8da39b',
    marginTop: 6,
  },
  actions: {
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  reportButton: {
    backgroundColor: '#f2b155',
    borderRadius: 10,
    paddingVertical: 8,
    paddingHorizontal: 16,
    alignItems: 'center',
    alignSelf: 'center',
    minWidth: 120,
  },
  reportText: {
    color: '#1b1b1b',
    fontSize: 12,
    fontWeight: '700',
    letterSpacing: 0.5,
  },
  reportPanel: {
    backgroundColor: '#11201e',
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: '#355e57',
  },
  reportPanelTitle: {
    color: '#f5f3e9',
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 10,
  },
  reportOptions: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  reportOption: {
    borderWidth: 1,
    borderColor: '#355e57',
    borderRadius: 12,
    paddingVertical: 8,
    paddingHorizontal: 10,
    backgroundColor: '#0f1c1a',
  },
  reportOptionActive: {
    backgroundColor: '#f2b155',
    borderColor: '#f2b155',
  },
  reportOptionText: {
    color: '#c6d4cf',
    fontSize: 12,
    fontWeight: '600',
  },
  reportOptionTextActive: {
    color: '#1b1b1b',
  },
  reportInstruction: {
    color: '#9cb0aa',
    fontSize: 12,
    marginTop: 10,
  },
  reportCancel: {
    alignSelf: 'flex-start',
    marginTop: 12,
  },
  reportCancelText: {
    color: '#f2b155',
    fontSize: 12,
    fontWeight: '600',
  },
  reportHint: {
    color: '#f2b155',
    fontSize: 12,
    marginTop: 8,
    textAlign: 'center',
  },
  reportPin: {
    width: 24,
    height: 24,
    borderRadius: 12,
    backgroundColor: '#f2b155',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: 2,
    borderColor: '#1b1b1b',
  },
  reportPinText: {
    color: '#1b1b1b',
    fontSize: 12,
    fontWeight: '700',
  },
  hint: {
    color: '#9cb0aa',
    marginTop: 10,
    fontSize: 12,
    textAlign: 'center',
  },
  permissionHint: {
    color: '#f2b155',
    paddingHorizontal: 20,
    paddingBottom: 12,
    textAlign: 'center',
    fontSize: 12,
  },
});
