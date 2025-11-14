package com.backend.helperClasses.dtos;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

import java.time.LocalDate;

@Getter
@Setter
public class PersonalInfoDto {

    @JsonProperty("full_name")
    private String fullName;

    @JsonProperty("date_of_birth")
    private LocalDate dateOfBirth;

    private String nationality;

    private ContactDto contact;
}
