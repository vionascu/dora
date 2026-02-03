FROM gradle:8.5-jdk21-jammy AS builder
WORKDIR /app
COPY ../.. .
RUN gradle :services:trail-service:build -x test --info

FROM openjdk:21-slim
WORKDIR /app
COPY --from=builder /app/services/trail-service/build/libs/*.jar app.jar
EXPOSE 8081
ENTRYPOINT ["java", "-jar", "app.jar"]
