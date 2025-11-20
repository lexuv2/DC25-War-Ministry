package com.backend.helperClasses.entities;

import java.time.LocalDate;
import java.util.UUID;

import com.backend.cv.entity.CV;
import com.fasterxml.jackson.annotation.JsonBackReference;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.ManyToOne;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
public class WorkExperience {

    @Id
    @GeneratedValue
    @Schema(description = "Unique work experience ID", example = "e5f6a7b8-cd34-5678-9012-bcdef1234567")
    private UUID id;

    @Schema(description = "Job title", example = "Software Engineer")
    private String jobTitle;

    @Schema(description = "Company name", example = "Google")
    private String company;

    @Schema(description = "Start date of employment", example = "2020-01-15")
    private LocalDate startDate;

    @Schema(description = "End date of employment", example = "2023-08-31")
    private LocalDate endDate;

    @JsonBackReference
    @ManyToOne
    private CV cv;
}
