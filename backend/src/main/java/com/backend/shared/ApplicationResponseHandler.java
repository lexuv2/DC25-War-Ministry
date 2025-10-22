package com.backend.shared;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

public class ApplicationResponseHandler {

    public static <T> ResponseEntity<Object> generateResponse(String message, HttpStatus status, T data) {

        final Map<String, Object> map = new HashMap<>();

        map.put("message", message);
        map.put("status", status);
        map.put("data", data);
        map.put("timestamp", LocalDateTime.now());

        return new ResponseEntity<>(map, status);
    }
}
