package com.backend.cv.controller.api;


import com.backend.cv.dto.PutCVRequest;
import com.backend.cv.entity.CV;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.responses.ApiResponse;
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

    @ApiResponse(responseCode = "200", description = "found the foo", content = {
            @Content(mediaType = "application/json", schema = @Schema(implementation = CV.class))})
    @GetMapping("/{id}")
    ResponseEntity<Object> getById(@PathVariable UUID id);

    @GetMapping
    ResponseEntity<Object> getAllSorted();

    @PutMapping("/{id}")
    ResponseEntity<Object> update(@RequestBody PutCVRequest cvRequest, @PathVariable UUID id);

    @DeleteMapping("/{id}")
    ResponseEntity<Object> delete(@PathVariable UUID id);
}
