package com.backend.mail.dto;

import jakarta.validation.constraints.NotBlank;

public record PutMailRequest(
        @NotBlank String emailAddress,
        @NotBlank boolean wasAccepted,
        String Reason,
        String MeetingDetails
) {
}
