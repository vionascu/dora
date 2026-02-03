package com.trailequip.weather.adapter.rest;

import com.trailequip.weather.application.service.WeatherApplicationService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import java.time.LocalDate;
import java.util.Map;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/v1/weather")
@Tag(name = "Weather", description = "Weather forecasts")
public class WeatherController {

    private final WeatherApplicationService weatherService;

    public WeatherController(WeatherApplicationService weatherService) {
        this.weatherService = weatherService;
    }

    @GetMapping("/forecast")
    @Operation(summary = "Get weather forecast")
    public ResponseEntity<Map<String, Object>> getForecast(
            @RequestParam double lat,
            @RequestParam double lon,
            @RequestParam String startDate,
            @RequestParam String endDate,
            @RequestParam(defaultValue = "Europe/Bucharest") String timezone) {
        Map<String, Object> forecast =
                weatherService.getForecast(lat, lon, LocalDate.parse(startDate), LocalDate.parse(endDate), timezone);
        return ResponseEntity.ok(forecast);
    }

    @GetMapping("/providers")
    @Operation(summary = "List weather providers")
    public ResponseEntity<Map<String, Object>> listProviders() {
        return ResponseEntity.ok(Map.of(
                "providers", new Object[] {Map.of("id", "open-meteo", "name", "Open-Meteo", "status", "active")}));
    }
}
