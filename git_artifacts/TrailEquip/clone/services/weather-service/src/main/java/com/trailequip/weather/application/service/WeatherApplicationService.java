package com.trailequip.weather.application.service;

import java.time.LocalDate;
import java.time.ZoneId;
import java.time.ZonedDateTime;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

@Service
public class WeatherApplicationService {

    private final RestTemplate restTemplate;

    public WeatherApplicationService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @Cacheable(value = "weatherForecast", key = "#lat + '-' + #lon + '-' + #startDate + '-' + #endDate")
    public Map<String, Object> getForecast(
            double lat, double lon, LocalDate startDate, LocalDate endDate, String timezone) {
        try {
            String url = String.format(
                    "https://api.open-meteo.com/v1/forecast?latitude=%f&longitude=%f&start_date=%s&end_date=%s&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max&timezone=%s",
                    lat, lon, startDate, endDate, timezone);

            Map<String, Object> response = restTemplate.getForObject(url, Map.class);

            return Map.of(
                    "location",
                    Map.of("latitude", lat, "longitude", lon),
                    "forecastData",
                    response != null ? response.getOrDefault("daily", Map.of()) : Map.of(),
                    "provider",
                    "open-meteo",
                    "cached",
                    false,
                    "cacheValidUntil",
                    ZonedDateTime.now(ZoneId.of("UTC")).plusHours(6).toString());
        } catch (Exception e) {
            return Map.of("error", "Unable to fetch forecast", "message", e.getMessage(), "cached", true);
        }
    }

    @Cacheable(value = "weatherForecast", key = "#lat + '-' + #lon")
    public Map<String, Object> getWeatherForecast(double lat, double lon) {
        LocalDate today = LocalDate.now();
        return getForecast(lat, lon, today, today.plusDays(7), "UTC");
    }

    public Map<String, Object> getCacheStatistics() {
        return Map.of(
                "cacheRegions", List.of("weatherForecast"),
                "estimatedSize", "N/A",
                "lastUpdated", ZonedDateTime.now().toString());
    }

    @CacheEvict(value = "weatherForecast", allEntries = true)
    public void clearCache() {
        // Cache will be cleared by Spring
    }

    public Map<String, Object> getWeatherForMultipleLocations(List<double[]> coordinates, LocalDate startDate) {
        Map<String, Object> allForecasts = new HashMap<>();
        for (double[] coord : coordinates) {
            String key = coord[0] + "," + coord[1];
            allForecasts.put(key, getForecast(coord[0], coord[1], startDate, startDate.plusDays(7), "UTC"));
        }
        return allForecasts;
    }
}
