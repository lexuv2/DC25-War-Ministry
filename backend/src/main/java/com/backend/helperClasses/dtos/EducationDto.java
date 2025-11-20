package com.backend.helperClasses.dtos;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDate;

@Getter
@Setter
public class EducationDto {

    private String degree;
    private String institution;

    @JsonProperty("start_date")
    private LocalDate startDate;

    @JsonProperty("end_date")
    private LocalDate endDate; // null allowed

    @JsonProperty("field_of_study")
    private String fieldOfStudy;
}
