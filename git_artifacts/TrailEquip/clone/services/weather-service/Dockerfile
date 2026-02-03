FROM gradle:8.5-jdk21-jammy AS builder
WORKDIR /app
COPY ../.. .
RUN gradle :services:weather-service:build -x test --info

FROM openjdk:21-slim
WORKDIR /app
COPY --from=builder /app/services/weather-service/build/libs/*.jar app.jar
EXPOSE 8082
ENTRYPOINT ["java", "-jar", "app.jar"]
