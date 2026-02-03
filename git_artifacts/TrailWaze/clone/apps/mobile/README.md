# Trailwaze Mobile App

Expo / React Native app.

Offline-first hiking navigation inspired by Waze.

## Getting started

```bash
npm install
npx expo start
```

## Web usage

```bash
npx expo start --web
```

The web interface uses OpenStreetMap tiles with a hiking trails overlay.

### Reporting guide (step-by-step)

1) Click "Raporteaza".
2) Choose a report type.
3) Click the map to place a pin.
4) Repeat to add more reports.

Pins are stored in memory for the current session.

## Tests

```bash
npm test
```

## E2E (Detox)

Detox uses native builds generated via Expo prebuild.

```bash
# iOS
npm run e2e:build:ios
npm run e2e:test:ios

# Android
npm run e2e:build:android
npm run e2e:test:android
```

## Offline maps (MBTiles)

The Bucegi region tileset lives at:

`apps/mobile/assets/RegionMaps/bucegi.mbtiles`

Bounds: `25.25, 45.28, 25.60, 45.52` (minLon, minLat, maxLon, maxLat)  
Zooms: `10-16`

The app loads this MBTiles file into the device file system on startup and
renders it with MapLibre.

Note: MBTiles rendering requires native iOS/Android builds. The web build uses
online tiles instead.
