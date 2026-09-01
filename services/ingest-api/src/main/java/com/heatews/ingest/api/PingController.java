package com.heatews.ingest.api;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
@RequestMapping("/api/v1")
public class PingController {

    private final JdbcTemplate jdbc;

    public PingController(JdbcTemplate jdbc) {
        this.jdbc = jdbc;
    }

    @GetMapping("/ping")
    public Map<String, Object> ping() {
        String postgis = jdbc.queryForObject("SELECT postgis_version()", String.class);
        return Map.of("status", "ok", "postgis", postgis);
    }
}
