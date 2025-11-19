package com.backend.helperClasses.dtos;

import lombok.Getter;
import lombok.Setter;

@Getter
@Setter
public class LanguageDto {

    private String language;
    private String proficiency; // enum values as string
}
