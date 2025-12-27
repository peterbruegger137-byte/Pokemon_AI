plugins {
    kotlin("jvm") version "1.9.25"
    kotlin("plugin.spring") version "1.9.25"
    id("org.springframework.boot") version "3.4.1" 
    id("io.spring.dependency-management") version "1.1.7"
}

group = "com.pokeai"
version = "0.0.1-SNAPSHOT"

java {
    toolchain {
        // Falls du Java 21 installierst, ändere dies auf 21. 
        // Mit 25 wird es wahrscheinlich weiterhin den "FAILURE" geben.
        languageVersion = JavaLanguageVersion.of(21) 
    }
}

repositories {
    mavenCentral()
}

dependencies {
    // Dashboard & Web-Server (Reactive) 
    implementation("org.springframework.boot:spring-boot-starter-webflux")
    implementation("org.springframework.boot:spring-boot-starter-thymeleaf")
    
    // Datenbank & Big Data (R2DBC für PostgreSQL) 
    implementation("org.springframework.boot:spring-boot-starter-data-r2dbc")
    implementation("org.postgresql:postgresql")
    implementation("org.postgresql:r2dbc-postgresql")
    
    implementation("org.jetbrains.kotlin:kotlin-reflect")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
    implementation("io.r2dbc:r2dbc-h2")
    runtimeOnly("com.h2database:h2")
}

kotlin {
    compilerOptions {
        freeCompilerArgs.addAll("-Xjsr305=strict")
    }
}