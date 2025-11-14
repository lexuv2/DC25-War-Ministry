package com.backend.cv.dto;

import com.backend.helperClasses.dtos.*;
import com.fasterxml.jackson.annotation.JsonProperty;
import lombok.Getter;
import lombok.Setter;

import java.util.List;

@Getter
@Setter
public class CvDto {

    @JsonProperty("personal_info")
    private PersonalInfoDto personalInfo;

    private List<EducationDto> education;

    @JsonProperty("work_experience")
    private List<WorkExperienceDto> workExperience;

    private List<String> skills;

    private List<CertificationDto> certifications;

    private List<LanguageDto> languages;

    @JsonProperty("military_experience")
    private List<MilitaryExperienceDto> militaryExperience;
}
