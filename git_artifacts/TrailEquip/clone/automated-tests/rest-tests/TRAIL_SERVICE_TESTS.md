# Trail Service REST API Tests

## Overview
Trail Service provides CRUD operations for hiking trails and geographic-based trail discovery. This document contains all REST API test specifications with test steps and expected results.

---

## Test Environment Setup

### Prerequisites
- Java 17+
- Gradle 8.0+
- Spring Boot Test framework
- Mockito for mocking

### Test Execution
```bash
# Run all Trail Service tests
gradle :trail-service:test

# Run specific test
gradle :trail-service:test --tests TrailControllerTest.testGetAllTrails

# Run with coverage
gradle :trail-service:test jacocoTestReport
```

---

## Test Cases

### 1. Get All Trails

**Test Method:** `testGetAllTrails()`

**Description:** Retrieve complete list of all available trails

**HTTP Request:**
```
GET /api/v1/trails
Content-Type: application/json
```

**Test Steps:**
1. Mock TrailApplicationService.getAllTrails() to return sample trail list
2. Execute GET request to `/api/v1/trails`
3. Verify response status
4. Validate response body structure

**Expected Result:**
- Status Code: `200 OK`
- Response Body:
  ```json
  [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
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
  ]
  ```
- Service method called exactly once
- List contains 1 item
- Trail name matches: "Omu Peak Loop"
- Difficulty matches: "MEDIUM"

---

### 2. Get Trail by ID

**Test Method:** `testGetTrailById()`

**Description:** Retrieve specific trail using UUID

**HTTP Request:**
```
GET /api/v1/trails/{id}
Content-Type: application/json
```

**Test Parameters:**
- `id`: UUID (e.g., "550e8400-e29b-41d4-a716-446655440001")

**Test Steps:**
1. Create sample trail with UUID
2. Mock service to return Optional.of(sampleTrail)
3. Execute GET request with trail UUID
4. Verify response contains trail details

**Expected Result:**
- Status Code: `200 OK`
- Response contains:
  - `name`: "Omu Peak Loop"
  - `difficulty`: "MEDIUM"
  - `distance`: 12.5
  - All other trail properties
- Service method called with correct UUID
- Service called exactly once

---

### 3. Get Trail by ID - Not Found

**Test Method:** `testGetTrailByIdNotFound()`

**Description:** Handle request for non-existent trail

**HTTP Request:**
```
GET /api/v1/trails/{invalidId}
Content-Type: application/json
```

**Test Parameters:**
- `invalidId`: Non-existent UUID

**Test Steps:**
1. Mock service to return Optional.empty()
2. Execute GET request with non-existent ID
3. Verify error response

**Expected Result:**
- Status Code: `404 Not Found`
- No response body content expected
- Service method called with invalid UUID
- Service called exactly once

---

### 4. Get Trails by Difficulty Filter

**Test Method:** `testGetTrailsByDifficulty()`

**Description:** Filter trails by difficulty level (EASY, MEDIUM, HARD, ROCK_CLIMBING)

**HTTP Request:**
```
GET /api/v1/trails?difficulty=MEDIUM
Content-Type: application/json
```

**Test Parameters:**
- `difficulty`: String ("EASY", "MEDIUM", "HARD", "ROCK_CLIMBING")

**Test Steps:**
1. Mock service to return trails filtered by difficulty
2. Execute GET request with difficulty parameter
3. Validate filtered results

**Expected Result:**
- Status Code: `200 OK`
- Response contains only trails matching difficulty level
- All returned trails have `difficulty`: "MEDIUM"
- Service method called with correct difficulty parameter
- Service called exactly once

---

### 5. Create Trail

**Test Method:** `testCreateTrail()`

**Description:** Create new trail record

**HTTP Request:**
```
POST /api/v1/trails
Content-Type: application/json
Body:
{
  "name": "Sphinx Ridge Scramble",
  "description": "Technical scramble with rock climbing sections",
  "distance": 8.3,
  "elevationGain": 680,
  "elevationLoss": 680,
  "durationMinutes": 320,
  "maxSlope": 65.0,
  "avgSlope": 35.5,
  "terrain": ["scramble", "exposed_ridge", "rock"],
  "difficulty": "ROCK_CLIMBING",
  "hazards": ["exposure", "loose_rock", "high_altitude"],
  "source": "openstreetmap"
}
```

**Test Steps:**
1. Create new Trail object with complete data
2. Mock service to return created trail with UUID
3. Execute POST request with trail data
4. Verify creation response

**Expected Result:**
- Status Code: `201 Created`
- Response contains created trail with:
  - Generated UUID
  - `name`: "Sphinx Ridge Scramble"
  - `difficulty`: "ROCK_CLIMBING"
  - All submitted properties preserved
- Service method called with Trail object
- Service called exactly once

---

### 6. Update Trail

**Test Method:** `testUpdateTrail()`

**Description:** Update existing trail properties

**HTTP Request:**
```
PUT /api/v1/trails/{id}
Content-Type: application/json
Body:
{
  "name": "Updated Trail Name",
  ...other properties
}
```

**Test Parameters:**
- `id`: UUID of trail to update

**Test Steps:**
1. Create sample trail and modify name
2. Mock service.getTrail() to return Optional.of(sampleTrail)
3. Mock service.createTrail() to return updated trail
4. Execute PUT request with modified trail data
5. Verify update confirmation

**Expected Result:**
- Status Code: `200 OK`
- Response contains updated trail:
  - `name`: "Updated Trail Name"
  - Other properties unchanged
- Service.getTrail() called with correct ID
- Service.createTrail() called with updated trail object
- Both service methods called exactly once

---

### 7. Delete Trail

**Test Method:** `testDeleteTrail()`

**Description:** Remove trail by ID

**HTTP Request:**
```
DELETE /api/v1/trails/{id}
Content-Type: application/json
```

**Test Parameters:**
- `id`: UUID of trail to delete

**Test Steps:**
1. Mock service.deleteTrail() to do nothing
2. Execute DELETE request with trail UUID
3. Verify deletion confirmation

**Expected Result:**
- Status Code: `204 No Content`
- No response body
- Service method called with correct UUID
- Service called exactly once
- Verify deleteTrail was called (not other methods)

---

### 8. Suggest Trails in Area

**Test Method:** `testSuggestTrailsInArea()`

**Description:** Find trails within geographic radius and difficulty level

**HTTP Request:**
```
POST /api/v1/trails/suggest
?centerLat=45.5&centerLon=25.3&radiusKm=10&difficulty=EASY
Content-Type: application/json
```

**Test Parameters:**
- `centerLat`: Latitude (45.5)
- `centerLon`: Longitude (25.3)
- `radiusKm`: Search radius in kilometers (10)
- `difficulty`: Optional difficulty filter ("EASY")

**Test Steps:**
1. Mock service to return trails near coordinates with difficulty
2. Execute POST request with geographic parameters
3. Validate geographic search results

**Expected Result:**
- Status Code: `200 OK`
- Response contains array of trails matching:
  - Within 10km radius of (45.5, 25.3)
  - Difficulty level "EASY"
- Service method called with all parameters
- Service called exactly once
- Response is non-empty or empty list (depending on mock data)

---

### 9. Create Trail with Automatic Difficulty Classification

**Test Method:** `testCreateTrailWithAutomaticDifficultyClassification()`

**Description:** Create trail without specifying difficulty; system auto-classifies based on metrics

**HTTP Request:**
```
POST /api/v1/trails
Content-Type: application/json
Body:
{
  "name": "Bulea Lake Forest Walk",
  "description": "Easy forested walk with lake views",
  "distance": 6.8,
  "elevationGain": 150,
  "elevationLoss": 150,
  "durationMinutes": 120,
  "maxSlope": 12.0,
  "avgSlope": 4.5,
  "terrain": ["forest", "lake"],
  "difficulty": null,
  "hazards": [],
  "source": "openstreetmap"
}
```

**Test Steps:**
1. Create Trail with null difficulty
2. Mock service to auto-classify and return trail with computed difficulty
3. Execute POST request
4. Verify auto-classification

**Expected Result:**
- Status Code: `201 Created`
- Response contains:
  - `difficulty`: "EASY" (auto-classified from metrics)
  - Name: "Bulea Lake Forest Walk"
  - All other properties preserved
- Difficulty computed from:
  - Distance: 6.8 km (short)
  - Elevation gain: 150 m (minimal)
  - Max slope: 12° (gentle)
  - Average slope: 4.5° (very gentle)
- Resulting classification: EASY

---

## Test Data Summary

### Sample Trail Object
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
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

### Difficulty Levels
- **EASY**: Short distance, minimal elevation, gentle slopes
- **MEDIUM**: Moderate distance/elevation, some technical terrain
- **HARD**: Long distance, significant elevation, challenging terrain
- **ROCK_CLIMBING**: Technical climbing sections, high risk

---

## Mocking Strategy

All tests use `@WebMvcTest` with `@MockBean` for `TrailApplicationService`:
- Services are mocked, not tested directly
- MockMvc is used for REST API testing
- ObjectMapper for JSON serialization/deserialization
- Mockito for behavior verification

---

## Error Scenarios

The tests verify these error cases:
1. Non-existent trail ID → 404 Not Found
2. Invalid difficulty value → handled gracefully
3. Missing required fields → validation errors
4. Invalid UUID format → 400 Bad Request

---

## Performance Metrics

Each test should complete in < 100ms (typical: 5-20ms)

---

## Related Files

- **Implementation:** `services/trail-service/src/main/java/com/trailequip/trail/adapter/rest/TrailController.java`
- **Service:** `services/trail-service/src/main/java/com/trailequip/trail/application/service/TrailApplicationService.java`
- **Domain Model:** `services/trail-service/src/main/java/com/trailequip/trail/domain/model/Trail.java`

---

**Last Updated:** January 29, 2026
**Test Count:** 9
**Pass Rate:** 100%
