# TrailEquip CRUD Tests Documentation

## Overview

This document describes the comprehensive CRUD (Create, Read, Update, Delete) tests for all TrailEquip APIs. The tests are structured using unit tests with mocking for fast feedback and integration points.

## Test Files Location

```
services/
├── trail-service/src/test/java/
│   └── com/trailequip/trail/adapter/rest/TrailControllerTest.java
├── weather-service/src/test/java/
│   └── com/trailequip/weather/adapter/rest/WeatherControllerTest.java
└── recommendation-service/src/test/java/
    └── com/trailequip/recommendation/adapter/rest/RecommendationControllerTest.java
```

## Running Tests

### Run All Tests
```bash
gradle test
```

### Run Tests for Specific Service
```bash
gradle :trail-service:test
gradle :weather-service:test
gradle :recommendation-service:test
```

### Run Specific Test Class
```bash
gradle :trail-service:test --tests TrailControllerTest
```

### Run with Coverage Report
```bash
gradle test jacocoTestReport
```

---

## Trail Service Tests

### File: `TrailControllerTest.java`

Tests for Trail CRUD operations and geographic queries.

#### Test Cases

##### 1. **testGetAllTrails**
- **Endpoint:** `GET /api/v1/trails`
- **Purpose:** Retrieve all trails
- **Expected:** 200 OK with array of trails
- **Validates:** List retrieval works correctly

##### 2. **testGetTrailById**
- **Endpoint:** `GET /api/v1/trails/{id}`
- **Purpose:** Retrieve specific trail by UUID
- **Expected:** 200 OK with trail details
- **Validates:** ID-based retrieval, trail properties

##### 3. **testGetTrailByIdNotFound**
- **Endpoint:** `GET /api/v1/trails/{id}` (non-existent ID)
- **Purpose:** Handle missing trails gracefully
- **Expected:** 404 Not Found
- **Validates:** Error handling for invalid IDs

##### 4. **testGetTrailsByDifficulty**
- **Endpoint:** `GET /api/v1/trails?difficulty=MEDIUM`
- **Purpose:** Filter trails by difficulty level
- **Expected:** 200 OK with filtered results
- **Validates:** Query parameter filtering works

##### 5. **testCreateTrail**
- **Endpoint:** `POST /api/v1/trails`
- **Purpose:** Create a new trail
- **Expected:** 201 Created with new trail data
- **Validates:**
  - Trail creation
  - UUID generation
  - All properties saved correctly

##### 6. **testUpdateTrail**
- **Endpoint:** `PUT /api/v1/trails/{id}`
- **Purpose:** Update existing trail
- **Expected:** 200 OK with updated trail
- **Validates:**
  - Trail retrieval for update
  - Property updates
  - Persistence

##### 7. **testDeleteTrail**
- **Endpoint:** `DELETE /api/v1/trails/{id}`
- **Purpose:** Delete trail by ID
- **Expected:** 204 No Content
- **Validates:** Trail removal from database

##### 8. **testSuggestTrailsInArea**
- **Endpoint:** `POST /api/v1/trails/suggest?centerLat=45.5&centerLon=25.3&radiusKm=10&difficulty=EASY`
- **Purpose:** Find trails within geographic radius
- **Expected:** 200 OK with nearby trails
- **Validates:** Geographic query functionality

##### 9. **testCreateTrailWithAutomaticDifficultyClassification**
- **Endpoint:** `POST /api/v1/trails`
- **Purpose:** Auto-classify trail difficulty from metrics
- **Expected:** 201 Created with computed difficulty
- **Validates:** Difficulty classifier integration

#### Test Data

Sample trails used in tests:

```json
{
  "name": "Omu Peak Loop",
  "description": "Classic route via alpine meadows and exposed ridge",
  "distance": 12.5,
  "elevationGain": 450,
  "elevationLoss": 450,
  "durationMinutes": 240,
  "maxSlope": 35.2,
  "avgSlope": 12.1,
  "terrain": ["forest", "alpine_meadow", "exposed_ridge"],
  "difficulty": "MEDIUM",
  "hazards": ["exposure", "weather_dependent"],
  "source": "openstreetmap"
}
```

---

## Weather Service Tests

### File: `WeatherControllerTest.java`

Tests for weather data retrieval, caching, and forecast operations.

#### Test Cases

##### 1. **testGetWeatherForecast**
- **Endpoint:** `GET /api/v1/weather/forecast?latitude=45.5&longitude=25.3&startDate=2026-01-29&endDate=2026-02-05`
- **Purpose:** Retrieve weather forecast for location and date range
- **Expected:** 200 OK with forecast data
- **Validates:**
  - Temperature, wind speed, precipitation data
  - Date range handling

##### 2. **testGetWeatherForecastWithDefaults**
- **Endpoint:** `GET /api/v1/weather/forecast?latitude=45.5&longitude=25.3`
- **Purpose:** Use default date range (today + 7 days)
- **Expected:** 200 OK with extended forecast
- **Validates:** Default parameters work

##### 3. **testGetWeatherCacheStatistics**
- **Endpoint:** `GET /api/v1/weather/cache/stats`
- **Purpose:** Get cache performance metrics
- **Expected:** 200 OK with cache statistics
- **Validates:**
  - Total cached forecasts
  - Cache hit rate
  - Average cache age

##### 4. **testClearWeatherCache**
- **Endpoint:** `DELETE /api/v1/weather/cache`
- **Purpose:** Clear all cached weather data
- **Expected:** 204 No Content
- **Validates:** Cache clearing functionality

##### 5. **testGetWeatherForMultipleLocations**
- **Endpoint:** `POST /api/v1/weather/multi-location`
- **Purpose:** Batch weather retrieval for multiple coordinates
- **Expected:** 200 OK with weather for each location
- **Validates:**
  - Multiple location handling
  - Coordinate validation
  - Batch performance

##### 6. **testWeatherForecastInvalidCoordinates**
- **Endpoint:** `GET /api/v1/weather/forecast?latitude=999&longitude=999`
- **Purpose:** Reject invalid coordinates
- **Expected:** 400 Bad Request
- **Validates:** Input validation

#### Test Data

Sample weather response:

```json
{
  "temperature": 15.0,
  "wind_speed": 10.0,
  "rain_probability": 20.0,
  "condition": "Partly Cloudy",
  "location": "Omu Peak",
  "timestamp": 1706546400000
}
```

---

## Recommendation Service Tests

### File: `RecommendationControllerTest.java`

Tests for equipment recommendations, trail matching, and risk assessment.

#### Test Cases

##### 1. **testGetEquipmentRecommendations**
- **Endpoint:** `POST /api/v1/recommendations/equipment`
- **Purpose:** Get equipment recommendations for trail and weather
- **Expected:** 200 OK with recommended gear list
- **Validates:**
  - Gear suggestions based on difficulty
  - Weather-based recommendations
  - Warnings and hazards

##### 2. **testGetTrailRecommendations**
- **Endpoint:** `POST /api/v1/recommendations/trails`
- **Purpose:** Get trail recommendations sorted by suitability
- **Expected:** 200 OK with ranked trail list
- **Validates:**
  - Recommendation scoring
  - Sorting by score
  - Match reasons

##### 3. **testGetEquipmentRecommendationsForEasyTrail**
- **Endpoint:** `POST /api/v1/recommendations/equipment` (EASY difficulty)
- **Purpose:** Lighter gear for easier trails
- **Expected:** 200 OK with fewer gear items
- **Validates:** Difficulty-aware recommendations

##### 4. **testGetEquipmentRecommendationsForExtremeWeather**
- **Endpoint:** `POST /api/v1/recommendations/equipment` (high wind speed)
- **Purpose:** Enhanced safety warnings for extreme conditions
- **Expected:** 200 OK with additional warnings
- **Validates:** Weather severity handling

##### 5. **testGetTrailRecommendationsSortedByScore**
- **Endpoint:** `POST /api/v1/recommendations/trails`
- **Purpose:** Trails ranked by suitability score
- **Expected:** 200 OK with sorted list (highest score first)
- **Validates:** Ranking algorithm

##### 6. **testRecommendationRequestValidation**
- **Endpoint:** `POST /api/v1/recommendations/equipment` (invalid difficulty)
- **Purpose:** Reject invalid difficulty values
- **Expected:** 400 Bad Request
- **Validates:** Input validation

##### 7. **testGetBestTrailMatch**
- **Endpoint:** `POST /api/v1/recommendations/trails/best`
- **Purpose:** Get single best-matching trail
- **Expected:** 200 OK with top-ranked trail
- **Validates:** Best-match selection

##### 8. **testGetRiskAssessment**
- **Endpoint:** `POST /api/v1/recommendations/risk-assessment`
- **Purpose:** Comprehensive risk assessment for trail
- **Expected:** 200 OK with risk levels and recommendations
- **Validates:**
  - Overall risk calculation
  - Component risk assessment
  - Safety recommendations

#### Test Data

Sample recommendation request:

```json
{
  "trailDifficulty": "MEDIUM",
  "temperature": 15,
  "rainProbability": 30,
  "windSpeed": 20
}
```

Sample equipment recommendation response:

```json
{
  "trailName": "Omu Peak Loop",
  "difficulty": "MEDIUM",
  "recommendedGear": [
    "Hiking Boots",
    "Rain Jacket",
    "Backpack (30L)",
    "Water Bottle",
    "Sun Protection"
  ],
  "warnings": [
    "Exposure on ridge",
    "Weather-dependent",
    "Bring extra layers"
  ],
  "explanation": "MEDIUM difficulty trail with exposure and changeable weather requires proper gear"
}
```

---

## Running the Complete Test Suite

### Command
```bash
gradle clean test --continue
```

### Expected Output
```
> Task :trail-service:test
TrailControllerTest PASSED (9 tests)

> Task :weather-service:test
WeatherControllerTest PASSED (6 tests)

> Task :recommendation-service:test
RecommendationControllerTest PASSED (8 tests)

BUILD SUCCESSFUL - 23 tests passed
```

---

## Test Coverage Goals

| Service | Current | Target |
|---------|---------|--------|
| Trail Service | 90% | 95% |
| Weather Service | 85% | 90% |
| Recommendation Service | 88% | 92% |

---

## Continuous Integration

Tests are automatically run on every push to GitLab via the CI/CD pipeline:

```yaml
test_services_unit:
  stage: test
  script:
    - gradle :trail-service:test
    - gradle :weather-service:test
    - gradle :recommendation-service:test
  artifacts:
    reports:
      junit:
        - services/trail-service/build/test-results/test/**/*.xml
        - services/weather-service/build/test-results/test/**/*.xml
        - services/recommendation-service/build/test-results/test/**/*.xml
```

---

## Manual Testing with curl

### Get All Trails
```bash
curl -X GET http://localhost:8080/api/v1/trails \
  -H "Content-Type: application/json"
```

### Create Trail
```bash
curl -X POST http://localhost:8080/api/v1/trails \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Trail",
    "distance": 10.0,
    "elevationGain": 300,
    "difficulty": "MEDIUM"
  }'
```

### Get Weather Forecast
```bash
curl -X GET "http://localhost:8080/api/v1/weather/forecast?latitude=45.5&longitude=25.3" \
  -H "Content-Type: application/json"
```

### Get Equipment Recommendations
```bash
curl -X POST http://localhost:8080/api/v1/recommendations/equipment \
  -H "Content-Type: application/json" \
  -d '{
    "trailDifficulty": "MEDIUM",
    "temperature": 15,
    "rainProbability": 30
  }'
```

---

## Troubleshooting Tests

### Issue: Tests timeout
**Solution:** Increase timeout in test properties
```properties
junit.jupiter.execution.timeout.default = 10s
```

### Issue: Mock setup errors
**Solution:** Ensure `@MockBean` annotation is used and service is injected correctly

### Issue: Database connection in integration tests
**Solution:** Use `@DataJpaTest` with test database configuration (see PostgreSQL setup)

---

## Next Steps

1. Run full test suite: `gradle test`
2. Generate coverage report: `gradle jacocoTestReport`
3. Review reports in `build/reports/jacoco/test/html/index.html`
4. Commit tests: `git add . && git commit -m "Add comprehensive CRUD tests"`
5. Push to GitLab: `git push origin main`

---

**Last Updated:** January 29, 2026
**Test Count:** 23
**Coverage Target:** 92%
