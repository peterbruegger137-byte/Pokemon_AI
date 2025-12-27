plugins {
    kotlin("jvm") version "1.9.20"
    id("org.springframework.boot") version "3.2.0"
    id("io.spring.dependency-management") version "1.1.4"
    kotlin("plugin.spring") version "1.9.20"
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-webflux") // Reaktives Backend
    implementation("org.springframework.boot:spring-boot-starter-data-r2dbc") // Reaktive DB-Anbindung
    implementation("org.postgresql:postgresql") // Postgres Treiber
    implementation("org.postgresql:r2dbc-postgresql") // Reaktiver Postgres Treiber
    implementation("com.fasterxml.jackson.module:jackson-module-kotlin") // JSON Support
}