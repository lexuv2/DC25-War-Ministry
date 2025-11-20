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
public class Education {

    @Id
    @GeneratedValue
    @Schema(description = "Unique education entry ID", example = "b2e3c4d5-e678-1234-5678-abcdef012345")
    private UUID id;

    @Schema(description = "Degree obtained", example = "Bachelor of Science")
    private String degree;

    @Schema(description = "Institution name", example = "University of Warsaw")
    private String institution;

    @Schema(description = "Start date of education", example = "2015-10-01")
    private LocalDate startDate;

    @Schema(description = "End date of education", example = "2018-06-30")
    private LocalDate endDate;

    @Schema(description = "Field of study", example = "Computer Science")
    private String fieldOfStudy;

    @JsonBackReference
    @ManyToOne
    private CV cv;
}
