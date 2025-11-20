package com.backend.mail.controller.api;


import com.backend.Gmail.PutMailRequest;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

public interface MailController {

    @PutMapping
    ResponseEntity<Object> create(@RequestBody PutMailRequest mailRequest);

    @GetMapping("/{id}")
    ResponseEntity<Object> getById(@PathVariable UUID id);

    @GetMapping
    ResponseEntity<Object> getAll();

    @PutMapping("/{id}")
    ResponseEntity<Object> update(@RequestBody PutMailRequest mailRequest, @PathVariable UUID id);

    @DeleteMapping("/{id}")
    ResponseEntity<Object> delete(@PathVariable UUID id);
}
