package com.backend.helperClasses.dtos;

import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class CertificationDto {

    private String name;

    @JsonProperty("issuing_organization")
    private String issuingOrganization;
}
