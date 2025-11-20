package com.backend.cv.dto;

import com.fasterxml.jackson.annotation.JsonFormat;
import jakarta.validation.constraints.*;
import lombok.Builder;

import java.time.LocalDate;
import java.util.Map;
import java.util.UUID;


public record PutCVRequest(
        @NotEmpty String fullName,
        @JsonFormat(pattern = "yyyy-MM-dd") LocalDate dateOfBirth,
        @NotBlank String nationality,
        @NotBlank String email,
        @NotBlank String phone,
        String address
) {
}
