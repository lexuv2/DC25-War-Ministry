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
public class Certification {

    @Id
    @GeneratedValue
    @Schema(description = "Unique certification ID", example = "a1f2b3c4-d567-8901-2345-6789abcdef01")
    private UUID id;

    @Schema(description = "Name of the certification", example = "AWS Certified Solutions Architect")
    private String name;

    @Schema(description = "Organization issuing the certification", example = "Amazon Web Services")
    private String issuingOrganization;

    @JsonBackReference
    @ManyToOne
    private CV cv;
}
