package com.backend.helperClasses.entities;

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
public class Language {

    @Id
    @GeneratedValue
    @Schema(description = "Unique language entry ID", example = "c3d4e5f6-1234-5678-9abc-def012345678")
    private UUID id;

    @Schema(description = "Language name", example = "English")
    private String language;

    @Schema(description = "Proficiency level", example = "C1")
    private String proficiency;

    @JsonBackReference
    @ManyToOne
    private CV cv;
}