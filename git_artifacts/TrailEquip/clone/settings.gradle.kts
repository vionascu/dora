rootProject.name = "trail-equip"

include(":trail-service")
project(":trail-service").projectDir = file("services/trail-service")

include(":weather-service")
project(":weather-service").projectDir = file("services/weather-service")

include(":recommendation-service")
project(":recommendation-service").projectDir = file("services/recommendation-service")

include(":api-gateway")
project(":api-gateway").projectDir = file("services/api-gateway")
