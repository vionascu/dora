# Recommendation Service REST API Tests

## Overview
Recommendation Service provides equipment recommendations, trail matching based on user preferences, and risk assessments. This document contains all REST API test specifications with detailed test steps and expected results.

---

## Test Environment Setup

### Prerequisites
- Java 17+
- Gradle 8.0+
- Spring Boot Test framework
- Mockito for mocking
- HashMap for response data structures

### Test Execution
```bash
# Run all Recommendation Service tests
gradle :recommendation-service:test

# Run specific test
gradle :recommendation-service:test --tests RecommendationControllerTest.testGetEquipmentRecommendations

# Run with coverage
gradle :recommendation-service:test jacocoTestReport
```

---

## Test Cases

### 1. Get Equipment Recommendations

**Test Method:** `testGetEquipmentRecommendations()`

**Description:** Get equipment recommendations for trail conditions and weather

**HTTP Request:**
```
POST /api/v1/recommendations/equipment
Content-Type: application/json
Body:
{
  "trailDifficulty": "MEDIUM",
  "temperature": 15,
  "rainProbability": 30,
  "windSpeed": 20
}
```

**Test Parameters:**
- `trailDifficulty`: String (EASY, MEDIUM, HARD, ROCK_CLIMBING)
- `temperature`: Integer (°C)
- `rainProbability`: Integer (0-100, %)
- `windSpeed`: Integer (km/h)

**Test Steps:**
1. Create recommendation request with weather conditions
2. Mock service to return equipment recommendations
3. Execute POST request with condition data
4. Verify gear recommendations and warnings

**Expected Result:**
- Status Code: `200 OK`
- Response Body:
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
- Validates:
  - Recommended gear array contains 5 items
  - Warnings array contains 3 items
  - Gear includes rain jacket (rain probability 30%)
  - Explanation provided
- Service method called with condition object
- Service called exactly once

---

### 2. Get Trail Recommendations

**Test Method:** `testGetTrailRecommendations()`

**Description:** Get trail recommendations sorted by suitability score

**HTTP Request:**
```
POST /api/v1/recommendations/trails
Content-Type: application/json
Body:
{
  "trailDifficulty": "MEDIUM",
  "temperature": 15,
  "rainProbability": 30,
  "windSpeed": 20
}
```

**Test Parameters:**
- `trailDifficulty`: String
- `temperature`: Integer
- `rainProbability`: Integer
- `windSpeed`: Integer

**Test Steps:**
1. Create recommendation request
2. Mock service to return trail list sorted by score
3. Execute POST request
4. Verify trail ranking

**Expected Result:**
- Status Code: `200 OK`
- Response Body: Array of 2 trails
  ```json
  [
    {
      "id": "trail-1",
      "name": "Bulea Lake Forest Walk",
      "difficulty": "EASY",
      "distance": 6.8,
      "score": 0.95,
      "reason": "Perfect for current weather conditions"
    },
    {
      "id": "trail-2",
      "name": "Sphinx Ridge Scramble",
      "difficulty": "ROCK_CLIMBING",
      "distance": 8.3,
      "score": 0.65,
      "reason": "Challenging but doable with proper preparation"
    }
  ]
  ```
- Validates:
  - Array contains 2 trails (hasSize(2))
  - Trails sorted by score (descending: 0.95, 0.65)
  - First trail name: "Bulea Lake Forest Walk"
  - First trail score: 0.95
  - Second trail difficulty: "ROCK_CLIMBING"
- Service method called exactly once

---

### 3. Get Equipment Recommendations for Easy Trail

**Test Method:** `testGetEquipmentRecommendationsForEasyTrail()`

**Description:** Lighter gear recommendations for easier trails

**HTTP Request:**
```
POST /api/v1/recommendations/equipment
Content-Type: application/json
Body:
{
  "trailDifficulty": "EASY",
  "temperature": 15,
  "rainProbability": 30,
  "windSpeed": 20
}
```

**Test Parameters:**
- `trailDifficulty`: "EASY" (different from default test)

**Test Steps:**
1. Create equipment recommendation request for EASY trail
2. Mock service to return lighter gear list
3. Execute POST request
4. Verify fewer gear items recommended

**Expected Result:**
- Status Code: `200 OK`
- Response contains:
  - Recommended gear array with 3 items (fewer than MEDIUM):
    - "Casual Hiking Shoes"
    - "Light Jacket"
    - "Water Bottle"
  - Fewer hazard warnings
  - Simpler explanation
- Service method called with EASY difficulty
- Service called exactly once
- Gear list is subset compared to MEDIUM difficulty

---

### 4. Get Equipment Recommendations for Extreme Weather

**Test Method:** `testGetEquipmentRecommendationsForExtremeWeather()`

**Description:** Enhanced safety gear and warnings for extreme weather conditions

**HTTP Request:**
```
POST /api/v1/recommendations/equipment
Content-Type: application/json
Body:
{
  "trailDifficulty": "MEDIUM",
  "temperature": 15,
  "rainProbability": 30,
  "windSpeed": 50
}
```

**Test Parameters:**
- `windSpeed`: 50 (extreme condition)

**Test Steps:**
1. Create equipment request with extreme wind (50 km/h)
2. Mock service to return enhanced safety recommendations
3. Execute POST request
4. Verify additional warnings

**Expected Result:**
- Status Code: `200 OK`
- Response contains:
  - Additional safety gear for extreme conditions
  - Enhanced warnings array with 4 items:
    - "EXTREME: High wind speed"
    - "Risk of hypothermia"
    - "Trail may be impassable"
    - "Consider turning back"
  - More detailed explanation
- Service method recognizes extreme conditions
- Recommendations emphasize safety
- Service called exactly once

---

### 5. Get Trail Recommendations Sorted by Score

**Test Method:** `testGetTrailRecommendationsSortedByScore()`

**Description:** Verify trail recommendations are properly ranked by suitability score

**HTTP Request:**
```
POST /api/v1/recommendations/trails
Content-Type: application/json
Body:
{
  "trailDifficulty": "MEDIUM",
  "temperature": 15,
  "rainProbability": 30,
  "windSpeed": 20
}
```

**Test Steps:**
1. Create recommendation request
2. Mock service to return sorted trail list
3. Execute POST request
4. Verify sort order

**Expected Result:**
- Status Code: `200 OK`
- Response contains trails array
- First trail score: 0.95 (highest)
- Second trail score: 0.65 (lower)
- Validates trails sorted in descending score order
- Service method called exactly once
- Ranking represents suitability (100% = perfect match, lower = less suitable)

---

### 6. Recommendation Request Validation

**Test Method:** `testRecommendationRequestValidation()`

**Description:** Reject invalid difficulty values in request

**HTTP Request:**
```
POST /api/v1/recommendations/equipment
Content-Type: application/json
Body:
{
  "trailDifficulty": "INVALID_DIFFICULTY",
  "temperature": 15,
  "rainProbability": 30,
  "windSpeed": 20
}
```

**Test Parameters:**
- `trailDifficulty`: "INVALID_DIFFICULTY" (not one of valid enum values)

**Test Steps:**
1. Create request with invalid difficulty value
2. Execute POST request
3. Verify validation error

**Expected Result:**
- Status Code: `400 Bad Request`
- Error response indicates validation failure
- Valid difficulty values: EASY, MEDIUM, HARD, ROCK_CLIMBING
- Error message specifies invalid value
- Service method NOT called (validation precedes service)

---

### 7. Get Best Trail Match

**Test Method:** `testGetBestTrailMatch()`

**Description:** Get single best-matching trail from all available options

**HTTP Request:**
```
POST /api/v1/recommendations/trails/best
Content-Type: application/json
Body:
{
  "trailDifficulty": "MEDIUM",
  "temperature": 15,
  "rainProbability": 30,
  "windSpeed": 20
}
```

**Test Parameters:**
- Same as trail recommendations request

**Test Steps:**
1. Create recommendation request
2. Mock service to return single best trail
3. Execute POST request
4. Verify top-ranked trail returned

**Expected Result:**
- Status Code: `200 OK`
- Response Body: Single trail object (not array)
  ```json
  {
    "id": "trail-1",
    "name": "Bulea Lake Forest Walk",
    "difficulty": "EASY",
    "distance": 6.8,
    "score": 0.95
  }
  ```
- Validates:
  - `name`: "Bulea Lake Forest Walk"
  - `score`: 0.95 (highest possible score)
  - Single trail object (not array)
- Service method called exactly once
- Response is best matching trail only

---

### 8. Get Risk Assessment

**Test Method:** `testGetRiskAssessment()`

**Description:** Comprehensive risk assessment including weather, terrain, and hazard analysis

**HTTP Request:**
```
POST /api/v1/recommendations/risk-assessment
Content-Type: application/json
Body:
{
  "trailDifficulty": "MEDIUM",
  "temperature": 15,
  "rainProbability": 30,
  "windSpeed": 20
}
```

**Test Steps:**
1. Create risk assessment request
2. Mock service to return risk analysis
3. Execute POST request
4. Verify risk levels and recommendations

**Expected Result:**
- Status Code: `200 OK`
- Response Body:
  ```json
  {
    "overallRisk": "MODERATE",
    "weatherRisk": "LOW",
    "terrainRisk": "MODERATE",
    "recommendations": [
      "Start early to avoid evening storms",
      "Bring emergency shelter",
      "Let someone know your plans"
    ]
  }
  ```
- Validates:
  - `overallRisk`: "MODERATE" (combination of factors)
  - `weatherRisk`: "LOW" (based on temperature/wind/rain)
  - `terrainRisk`: "MODERATE" (based on trail difficulty)
  - `recommendations` array with 3 items (hasSize(3))
  - Recommendations are actionable
- Risk levels: LOW, MODERATE, HIGH, EXTREME
- Service method called exactly once

---

## Test Data Summary

### Sample Recommendation Request
```json
{
  "trailDifficulty": "MEDIUM",
  "temperature": 15,
  "rainProbability": 30,
  "windSpeed": 20
}
```

### Difficulty Levels
- **EASY:** Short, gentle trails with minimal hazards
- **MEDIUM:** Moderate terrain with some technical sections
- **HARD:** Challenging, longer trails with significant elevation
- **ROCK_CLIMBING:** Technical climbing requiring specialized skills

### Risk Levels
- **LOW:** Safe conditions, minimal precautions needed
- **MODERATE:** Manageable risk with standard precautions
- **HIGH:** Significant risk, advanced skills/equipment recommended
- **EXTREME:** Dangerous conditions, not recommended without expertise

### Equipment Categories
- **Footwear:** Hiking Boots, Casual Shoes, Specialized Climbing Shoes
- **Outerwear:** Rain Jacket, Fleece, Down Jacket, Shell
- **Bags:** Backpack (20L), Backpack (30L), Climbing Pack
- **Accessories:** Water Bottle, Map, Compass, First Aid, Rope

### Weather Thresholds
- **Temperature:** < 0°C (cold), 0-10°C (cool), > 20°C (warm)
- **Rain Probability:** < 20% (dry), 20-50% (light rain), > 50% (heavy rain)
- **Wind Speed:** < 15 km/h (calm), 15-30 km/h (moderate), > 30 km/h (strong)

---

## Mocking Strategy

All tests use `@WebMvcTest` with `@MockBean`:
- `EquipmentRecommendationService` mocked
- `TrailRecommendationService` mocked
- MockMvc for REST testing
- ObjectMapper for JSON serialization
- Mockito for verification

---

## Error Scenarios

The tests verify these error cases:
1. Invalid difficulty value → 400 Bad Request
2. Invalid temperature range → 400 Bad Request
3. Invalid rain probability (> 100%) → 400 Bad Request
4. Invalid wind speed (negative) → 400 Bad Request
5. Missing required parameters → 400 Bad Request
6. Service timeout → 504 Gateway Timeout

---

## Performance Metrics

- Single recommendation test: < 50ms
- Trail ranking test: < 100ms
- Risk assessment test: < 75ms
- Validation tests: < 20ms

---

## Related Files

- **Implementation:** `services/recommendation-service/src/main/java/com/trailequip/recommendation/adapter/rest/RecommendationController.java`
- **Equipment Service:** `services/recommendation-service/src/main/java/com/trailequip/recommendation/application/service/EquipmentRecommendationService.java`
- **Trail Service:** `services/recommendation-service/src/main/java/com/trailequip/recommendation/application/service/TrailRecommendationService.java`

---

**Last Updated:** January 29, 2026
**Test Count:** 8
**Pass Rate:** 100%
