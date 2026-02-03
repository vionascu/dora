# Trailwaze MVP - Epics, User Stories, Acceptance Criteria

## Epic 1: Mobile app foundation (React Native + Expo)

### US1.1 - As a user, I want to launch the app on my phone
Acceptance criteria:
- The app starts via `npx expo start` without errors.
- The initial screen shows the app title and a basic layout.

### US1.2 - As a developer, I want a minimal repo structure
Acceptance criteria:
- A functional Expo project exists in `apps/mobile`.
- `npm install` and `npx expo start` are documented in the README.

## Epic 2: Offline maps (MapLibre + MBTiles)

### US2.1 - As a user, I want to see an offline map
Acceptance criteria:
- The map loads without an internet connection.
- Tile sources are local MBTiles.

### US2.2 - As a user, I want to see my position on the map
Acceptance criteria:
- The GPS dot appears on the map.
- If GPS permission is denied, the app shows a clear message.

### US2.3 - As a user, I want to see GPX tracks
Acceptance criteria:
- GPX tracks can be displayed on the map.
- The track remains visible offline.

### US2.4 - As a user, I want themed layers (bear, ice, obstacles)
Acceptance criteria:
- Layers can be toggled on/off.
- Layers render offline.

## Epic 3: Local storage (reports, cache, sync)

### US3.1 - As a user, I want to save reports locally
Acceptance criteria:
- Reports are stored in local SQLite.
- Minimum fields: id, type, lat, lon, createdAt, expiresAt.

### US3.2 - As a user, I want caching for tracks and reports
Acceptance criteria:
- Tracks and reports can be read offline from cache.
- Cache can be invalidated after a configurable period.

### US3.3 - As a user, I want a sync queue
Acceptance criteria:
- A `syncQueue` table exists with status and retries.
- Queue items are processed when connectivity is available.

## Epic 4: Fast backend for sync (Supabase/Firebase)

### US4.1 - As a user, I want automatic sync when signal returns
Acceptance criteria:
- Reports in `syncQueue` are sent to the backend when online.
- If sync fails, status updates and retries occur.

### US4.2 - As a user, I want new reports from my area
Acceptance criteria:
- The app can query reports within a geographic radius.
- The app can filter reports from the last 24h.

## Epic 5: Weather, wind, alerts

### US5.1 - As a user, I want a simple forecast for key points
Acceptance criteria:
- The app can display weather for predefined coordinates.
- Data is cached locally to reduce API calls.

### US5.2 - As a user, I want essential alerts at route level
Acceptance criteria:
- Alerts appear in the UI when new data exists.
- Alerts update only when connectivity is available.

## Epic 6: Waze-style reporting without signal

### US6.1 - As a user, I want a fast reporting button
Acceptance criteria:
- A visible "Report" button exists.
- The report auto-captures coordinates and time.

### US6.2 - As a user, I want to choose the report type
Acceptance criteria:
- Available types: bear, ice, fallen tree, scree, hut full.
- The chosen type is saved in the report.

### US6.3 - As a user, I want to add a photo and text
Acceptance criteria:
- Photo is optional and stored locally.
- Short text is optional and stored locally.

### US6.4 - As a user, I want automatic expiration (TTL)
Acceptance criteria:
- Reports have `expiresAt` set based on type.
- Expired reports are no longer shown.
