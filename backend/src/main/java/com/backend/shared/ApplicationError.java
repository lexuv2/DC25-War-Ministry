package com.backend.shared;

import lombok.Getter;
import org.springframework.http.HttpStatus;

@Getter
public class ApplicationError extends RuntimeException {
    private final HttpStatus status;
    private String message = "Application error";

    public ApplicationError(HttpStatus status) {
        super(status.name());
        this.status = status;
    }

    public ApplicationError(HttpStatus status, String message) {
        super(status.name());
        this.status = status;
        this.message = message;
    }
}
