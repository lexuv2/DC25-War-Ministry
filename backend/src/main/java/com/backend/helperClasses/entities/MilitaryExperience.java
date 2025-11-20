package com.backend.helperClasses.entities;

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

import com.backend.cv.entity.CV;
import com.fasterxml.jackson.annotation.JsonBackReference;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
public class MilitaryExperience {

    @Id
    @GeneratedValue
    @Schema(description = "Unique military experience ID", example = "d4e5f6a7-bc12-3456-7890-abcdef123456")
    private UUID id;

    @Schema(description = "Military rank", example = "Sergeant")
    private String rank;

    @Schema(description = "Branch of service", example = "Land Forces")
    private String branch;

    @Schema(description = "Service start date", example = "2014-03-01")
    private LocalDate startDate;

    @Schema(description = "Service end date", example = "2016-09-15")
    private LocalDate endDate;

    @ElementCollection
    @Schema(description = "List of main duties", example = "[\"Logistics coordination\", \"Team supervision\"]")
    private List<String> duties;

    @JsonBackReference
    @ManyToOne
    private CV cv;
}
