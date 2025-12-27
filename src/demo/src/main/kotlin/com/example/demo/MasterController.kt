package com.example.demo

import org.springframework.data.annotation.Id
import org.springframework.data.relational.core.mapping.Table
import org.springframework.data.repository.reactive.ReactiveCrudRepository
import org.springframework.stereotype.Controller
import org.springframework.ui.Model
import org.springframework.web.bind.annotation.*
import org.springframework.r2dbc.core.DatabaseClient
import org.springframework.http.HttpStatus
import org.springframework.http.server.reactive.ServerHttpResponse
import reactor.core.publisher.Mono
import java.io.File
import java.time.LocalDateTime
import java.net.URI
import jakarta.annotation.PostConstruct

// Haupt-Statistiken (Erweitert um Juggernaut-Daten)
@Table("training_stats")
data class TrainingStats(
    @Id val id: Long? = null,
    val timesteps: Int = 0,
    val reward: Double = 0.0,
    val agentId: String = "unknown",
    val fps: Double = 0.0,
    val learningRate: Double = 0.0,
    val entropy: Double = 0.0,
    val exploreScore: Int = 0,
    val currentLocation: String? = "unknown",
    val battlesWon: Int = 0,
    val wallCollisions: Int = 0,         // NEU: Tracking für Stuck-Detection
    val epsilon: Double = 0.0,
    val timestamp: LocalDateTime = LocalDateTime.now()
)

// Modell für das geografische Gedächtnis (Map Knowledge)
@Table("map_knowledge")
data class MapKnowledge(
    @Id val id: Long? = null,
    val locationHash: String,
    val areaType: String? = "land",      // NEU: Gras oder Wasser
    val xpYield: Double,
    val timestamp: LocalDateTime = LocalDateTime.now()
)

// Modell für die Pokémon-Effizienz & Analytics
data class AnalyticsPayload(
    val agentId: String,
    val pokemonEfficiencies: Map<String, String> = emptyMap(),
    val locationHotspots: Map<String, Int> = emptyMap(),
    val type: String? = null,
    val location: String? = null,
    val areaType: String? = null,        // NEU: Übermittlung Gras/Wasser
    val xpGain: Double? = null,
    val reward: Double? = null,
    val penaltyType: String? = null
)

interface StatsRepository : ReactiveCrudRepository<TrainingStats, Long>
interface MapKnowledgeRepository : ReactiveCrudRepository<MapKnowledge, Long>

@Controller
class MasterController(
    val repository: StatsRepository, 
    val mapRepo: MapKnowledgeRepository,
    val dbClient: DatabaseClient
) {
    private var activeProcess: Process? = null
    private var lastAnalytics: AnalyticsPayload? = null

    @PostConstruct
    fun init() {
        println("\n" + "#".repeat(50))
        println("✅ MASTERCONTROLLER MULTI-MONITORING BEREIT")
        println("🌐 Juggernaut-Tracking & Map-Memory aktiv")
        println("#".repeat(50) + "\n")

        // SCHEMA FIX: Erstellt Tabellen mit ALLEN notwendigen Spalten beim Start
        dbClient.sql("""
            CREATE TABLE IF NOT EXISTS training_stats (
                id IDENTITY PRIMARY KEY, timesteps INT, reward DOUBLE, agent_id VARCHAR(255), 
                fps DOUBLE, learning_rate DOUBLE, entropy DOUBLE, explore_score INT, 
                current_location VARCHAR(50), battles_won INT DEFAULT 0, 
                wall_collisions INT DEFAULT 0, epsilon DOUBLE DEFAULT 0.0, timestamp TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS map_knowledge (
                id IDENTITY PRIMARY KEY, location_hash VARCHAR(50), area_type VARCHAR(20), 
                xp_yield DOUBLE, timestamp TIMESTAMP
            );
        """).then().subscribe() 
    }

    @GetMapping("/")
    fun index(model: Model): Mono<String> {
        model.addAttribute("isRunning", activeProcess?.isAlive ?: false)
        
        val backupFolder = File("C:/Users/Peter/Desktop/Gameboy")
        val stateFiles = backupFolder.listFiles { _, name -> name.endsWith(".sgm") || name.contains(".sg") }
        model.addAttribute("backupCount", stateFiles?.size ?: 0)

        // BestehendefindAll Logik beibehalten
        return repository.findAll().collectList().flatMap { stats ->
            mapRepo.findAll().collectList().map { mapData ->
                val sorted = stats.sortedByDescending { it.timestamp }
                model.addAttribute("stats", sorted.take(15))
                model.addAttribute("mapKnowledge", mapData)
                if (sorted.isNotEmpty()) model.addAttribute("lastStat", sorted.first())
                "index"
            }
        }
    }

    @GetMapping("/api/history")
    @ResponseBody
    fun getHistory(): Mono<List<TrainingStats>> = repository.findAll().collectList().map { it.sortedBy { s -> s.timesteps } }

    @GetMapping("/api/map")
    @ResponseBody
    fun getMapData() = mapRepo.findAll()

    @PostMapping("/stats")
    @ResponseBody
    fun receiveStats(@RequestBody stats: TrainingStats): Mono<TrainingStats> {
        if (stats.timesteps % 1000 == 0) {
            println("📊 Step ${stats.timesteps} | Reward: ${stats.reward} | Stuck-Hits: ${stats.wallCollisions}")
        }
        return repository.save(stats.copy(timestamp = LocalDateTime.now()))
    }

    @PostMapping("/analytics")
    @ResponseBody
    fun receiveAnalytics(@RequestBody analytics: AnalyticsPayload): Mono<Void> {
        this.lastAnalytics = analytics
        
        return when (analytics.type) {
            "MAP_DATA" -> {
                mapRepo.save(MapKnowledge(
                    locationHash = analytics.location ?: "unknown",
                    areaType = analytics.areaType ?: "land",
                    xpYield = analytics.xpGain ?: 0.0
                )).then()
            }
            "EPISODE" -> {
                println("🏆 Juggernaut-Sieg! Bonus: ${analytics.reward}")
                Mono.empty()
            }
            "PENALTY" -> {
                println("⚠️ Strafe für: ${analytics.penaltyType}")
                Mono.empty()
            }
            else -> Mono.empty()
        }
    }

    @GetMapping("/api/analytics")
    @ResponseBody
    fun getAnalytics(): AnalyticsPayload? = lastAnalytics

    @PostMapping("/start")
    fun start(
        @RequestParam(value = "algo", defaultValue = "PPO") algo: String,
        @RequestParam(value = "lr", defaultValue = "0.0003") lrRaw: String,
        @RequestParam(value = "batchSize", defaultValue = "2048") batchSizeRaw: String,
        @RequestParam(value = "mode", defaultValue = "work") mode: String,
        response: ServerHttpResponse
    ): Mono<Void> {
        activeProcess?.let { if (it.isAlive) it.destroyForcibly() }

        return Mono.fromRunnable<Void> {
            try {
                val lr = lrRaw.replace(",", ".").toDouble()
                val batchSize = batchSizeRaw.toInt()
                
                val pb = ProcessBuilder("python", "pokemon_agend.py", 
                    "--algo", algo, "--lr", lr.toString(), "--batch_size", batchSize.toString(), "--mode", mode
                )
                
                pb.environment()["PYTHONIOENCODING"] = "utf-8"
                pb.directory(File("C:/Users/Peter/Desktop/Gameboy"))
                pb.inheritIO()
                activeProcess = pb.start()
                println("🚀 JUGGERNAUT GESTARTET: $algo")
            } catch (e: Exception) { println("❌ START-FEHLER: ${e.message}") }
        }.then(redirect(response))
    }

    @PostMapping("/stop")
    fun stop(response: ServerHttpResponse): Mono<Void> {
        activeProcess?.let { 
            if (it.isAlive) {
                println("🛑 Stoppe Training...")
                it.destroy() 
                Thread.sleep(1500)
                if (it.isAlive) it.destroyForcibly()
            }
        }
        return redirect(response)
    }

    private fun redirect(response: ServerHttpResponse): Mono<Void> {
        response.statusCode = HttpStatus.SEE_OTHER
        response.headers.location = URI.create("/")
        return response.setComplete()
    }
}