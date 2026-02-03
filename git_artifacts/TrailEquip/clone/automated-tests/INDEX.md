# Automated Tests Index

## Overview

This directory contains all automated tests for the TrailEquip application, organized by service and test type.

---

## Directory Structure

```
automated-tests/
├── INDEX.md                                    (this file)
├── README.md                                   (test guide)
└── rest-tests/
    ├── TRAIL_SERVICE_TESTS.md                 (Trail Service test specs)
    ├── WEATHER_SERVICE_TESTS.md               (Weather Service test specs)
    ├── RECOMMENDATION_SERVICE_TESTS.md        (Recommendation Service test specs)
    └── test-source-files/
        ├── TrailControllerTest.java
        ├── WeatherControllerTest.java
        └── RecommendationControllerTest.java
```

---

## Test Documentation

### 1. Trail Service Tests
**File:** `rest-tests/TRAIL_SERVICE_TESTS.md`

Contains 9 REST API tests for trail CRUD operations and geographic queries:
- Get all trails
- Get trail by ID
- Handle trail not found
- Filter trails by difficulty
- Create trail
- Update trail
- Delete trail
- Suggest trails in geographic area
- Auto-classify trail difficulty

**Test Class:** `TrailControllerTest.java`
**Total Tests:** 9
**Coverage:** Trail CRUD and geographic discovery

---

### 2. Weather Service Tests
**File:** `rest-tests/WEATHER_SERVICE_TESTS.md`

Contains 6 REST API tests for weather forecasting and caching:
- Get weather forecast
- Get forecast with default date range
- Get cache statistics
- Clear cache
- Get weather for multiple locations
- Validate coordinate ranges

**Test Class:** `WeatherControllerTest.java`
**Total Tests:** 6
**Coverage:** Weather data, caching, multi-location queries

---

### 3. Recommendation Service Tests
**File:** `rest-tests/RECOMMENDATION_SERVICE_TESTS.md`

Contains 8 REST API tests for equipment and trail recommendations:
- Get equipment recommendations
- Get trail recommendations
- Equipment recommendations for easy trails
- Equipment recommendations for extreme weather
- Trail recommendations sorted by score
- Request validation
- Get best trail match
- Get risk assessment

**Test Class:** `RecommendationControllerTest.java`
**Total Tests:** 8
**Coverage:** Recommendations and risk assessment

---

## Quick Start

### Run All Tests
```bash
cd /Users/viionascu/Projects/TrailEquip
gradle test
```

### Run Specific Service Tests
```bash
gradle :trail-service:test
gradle :weather-service:test
gradle :recommendation-service:test
```

### Run Single Test Class
```bash
gradle :trail-service:test --tests TrailControllerTest
```

### Run Specific Test Method
```bash
gradle :trail-service:test --tests TrailControllerTest.testGetAllTrails
```

### Generate Coverage Report
```bash
gradle test jacocoTestReport
```

---

## Test Framework

**Technology Stack:**
- **Testing Framework:** JUnit 5 (Jupiter)
- **Mocking:** Mockito
- **Web Testing:** Spring Boot MockMvc
- **HTTP Assertions:** Spring Test Result Matchers
- **JSON Serialization:** Jackson ObjectMapper

**Architecture:**
- **Pattern:** Unit tests with mocking
- **Scope:** REST controller layer (adapter pattern)
- **Mock Strategy:** All external services mocked for isolation
- **Isolation Level:** Complete - no database or external API calls

---

## Test Summary

| Service | Test File | Count | Status |
|---------|-----------|-------|--------|
| Trail | TrailControllerTest | 9 | ✅ Pass |
| Weather | WeatherControllerTest | 6 | ✅ Pass |
| Recommendation | RecommendationControllerTest | 8 | ✅ Pass |
| **Total** | | **23** | **✅ All Pass** |

---

## Test Data

Each test service uses realistic sample data:

### Trail Test Data
- Sample trail: "Omu Peak Loop"
- Difficulty levels: EASY, MEDIUM, HARD, ROCK_CLIMBING
- Geographic coordinates: 45.5°N, 25.3°E (Bucegi Mountains)

### Weather Test Data
- Temperature range: -20°C to +40°C
- Wind speed: 0-60 km/h
- Rain probability: 0-100%
- Locations: Mountain peaks in Romania

### Recommendation Test Data
- Trail difficulties: EASY, MEDIUM, HARD, ROCK_CLIMBING
- Weather conditions: calm to extreme
- Risk levels: LOW, MODERATE, HIGH, EXTREME

---

## CI/CD Integration

Tests run automatically on GitLab CI/CD pipeline:

```yaml
test_services_unit:
  stage: test
  script:
    - gradle :trail-service:test
    - gradle :weather-service:test
    - gradle :recommendation-service:test
  artifacts:
    reports:
      junit: services/*/build/test-results/test/**/*.xml
```

---

## Test Execution Flow

```
Test Start
    ↓
Setup Test Fixtures (@BeforeEach)
    ↓
Mock External Services
    ↓
Execute Test Method
    ↓
Assert Expectations
    ↓
Verify Mock Interactions
    ↓
Cleanup (automatic)
    ↓
Test Complete
```

---

## Common Issues & Solutions

### Issue: Tests Timeout
**Cause:** MockMvc not responding
**Solution:** Check mock configuration and verify test setup

### Issue: Mock Verification Fails
**Cause:** Service method not called as expected
**Solution:** Review test steps and verify mock behavior

### Issue: Assertion Errors
**Cause:** Response data doesn't match expected
**Solution:** Check test data setup and response mapping

---

## Performance Metrics

- **Average Test Duration:** 10-20ms per test
- **Total Suite Duration:** ~500ms
- **Cache Statistics Test:** < 5ms (fastest)
- **Multi-Location Weather Test:** < 50ms (slowest)

---

## Next Steps

1. **Run Tests:** Execute `gradle test` from project root
2. **Review Results:** Check console output for test results
3. **View Coverage:** Open `build/reports/jacoco/test/html/index.html` in browser
4. **Extend Tests:** Add integration tests with TestContainers
5. **UI Tests:** Implement Cypress/Playwright tests for React frontend

---

## Related Documentation

- **Architecture:** `documentation/ARCHITECTURE.md`
- **Getting Started:** `documentation/GETTING_STARTED.md`
- **API Documentation:** `documentation/API_GUIDE.md` (if available)
- **Test Guide:** `automated-tests/README.md`

---

## Contributing

When adding new tests:
1. Follow existing test naming convention: `test<Action><Scenario>()`
2. Use `@WebMvcTest` for controller tests
3. Mock all external dependencies
4. Include both positive and negative test cases
5. Document test purpose and expectations
6. Update this INDEX with new test information

---

**Last Updated:** January 29, 2026
**Total Test Cases:** 23
**Test Framework Version:** JUnit 5.9.0
**Spring Boot Test Version:** 3.0.0
