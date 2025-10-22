package com.backend.mail.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotEmpty;

import java.time.LocalDate;


public record PutMailRequest(
        @NotBlank String emailAddress
) {
}
