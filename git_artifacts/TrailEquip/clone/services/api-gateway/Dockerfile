FROM gradle:8.5-jdk21-jammy AS builder
WORKDIR /app
COPY ../.. .
RUN gradle :services:api-gateway:build -x test --info

FROM openjdk:21-slim
WORKDIR /app
COPY --from=builder /app/services/api-gateway/build/libs/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
