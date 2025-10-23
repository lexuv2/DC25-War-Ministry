package com.backend.Gmail;

import jakarta.validation.constraints.NotBlank;

public record PutMailRequest(
        @NotBlank String emailAddress,
        @NotBlank boolean wasAccepted,
        String Reason,
        String meetingDetails,
        String position
) {
}
