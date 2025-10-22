package com.backend.cv.controller.api;


import com.backend.cv.dto.PutCVRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;

import java.util.UUID;

public interface CVController {

    @PutMapping
    ResponseEntity<Object> create(@RequestBody PutCVRequest cvRequest);

    @GetMapping("/{id}")
    ResponseEntity<Object> getById(@PathVariable UUID id);

    @GetMapping
    ResponseEntity<Object> getAll();

    @PutMapping("/{id}")
    ResponseEntity<Object> update(@RequestBody PutCVRequest cvRequest, @PathVariable UUID id);

    @DeleteMapping("/{id}")
    ResponseEntity<Object> delete(@PathVariable UUID id);
}
