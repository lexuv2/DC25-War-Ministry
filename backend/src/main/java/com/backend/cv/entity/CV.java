package com.backend.cv.entity;

import com.backend.helperClasses.entities.*;
import com.fasterxml.jackson.annotation.JsonBackReference;
import com.fasterxml.jackson.annotation.JsonManagedReference;
import io.swagger.v3.oas.annotations.media.Schema;
import jakarta.persistence.*;
import lombok.*;

import java.io.Serializable;
import java.time.LocalDate;
import java.util.UUID;
import java.util.List;


@Getter
@Setter
@Entity
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CV implements Serializable {
    @Id
    @GeneratedValue
    @Schema(description = "Unique identifier of the CV", example = "c8a1b1d2-4e89-4f74-b2ad-1a3c9f54af12")
    private UUID id;

    @Schema(description = "Full name of the person", example = "John Doe")
    private String fullName;

    @Schema(description = "Position the candidate applies for", example = "operator wajchy")
    private String position;

    @Schema(description = "Date of birth", example = "1990-05-14")
    private LocalDate dateOfBirth;

    @Schema(description = "Nationality of the person", example = "Polish")
    private String nationality;

    @Schema(description = "Email address", example = "john.doe@example.com")
    private String email;

    @Schema(description = "Phone number", example = "+48 600 700 800")
    private String phone;

    @Schema(description = "Home address", example = "Warsaw, Poland")
    private String address;

    @JsonManagedReference
    @OneToMany(mappedBy = "cv", cascade = CascadeType.ALL)
    @Schema(description = "List of education entries")
    private List<Education> education;

    @JsonManagedReference
    @OneToMany(mappedBy = "cv", cascade = CascadeType.ALL)
    @Schema(description = "List of work experiences")
    private List<WorkExperience> workExperience;

    @JsonManagedReference
    @ElementCollection
    @Schema(description = "List of skills", example = "[\"Java\", \"Spring Boot\", \"SQL\"]")
    private List<String> skills;

    @JsonManagedReference
    @OneToMany(mappedBy = "cv", cascade = CascadeType.ALL)
    @Schema(description = "List of certifications")
    private List<Certification> certifications;

    @JsonManagedReference
    @OneToMany(mappedBy = "cv", cascade = CascadeType.ALL)
    @Schema(description = "List of languages")
    private List<Language> languages;

    @JsonManagedReference
    @OneToMany(mappedBy = "cv", cascade = CascadeType.ALL)
    @Schema(description = "List of military experiences")
    private List<MilitaryExperience> militaryExperience;

    @Schema(description = "Computed score evaluating this CV", example = "87")
    private int score;
}
