package com.backend.cv.entity;

import com.backend.helperClasses.entities.*;
import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDate;
import java.util.UUID;
import java.util.List;


@Getter
@Setter
@Entity
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CV {
    @Id
    @GeneratedValue
    private UUID id;

    private String fullName;
    private LocalDate dateOfBirth;
    private String nationality;

    private String email;
    private String phone;
    private String address;

    @OneToMany(mappedBy = "cv", cascade = CascadeType.ALL)
    private List<Education> education;

    @OneToMany(mappedBy = "cv", cascade = CascadeType.ALL)
    private List<WorkExperience> workExperience;

    @ElementCollection
    private List<String> skills;

    @OneToMany(mappedBy = "cv", cascade = CascadeType.ALL)
    private List<Certification> certifications;

    @OneToMany(mappedBy = "cv", cascade = CascadeType.ALL)
    private List<Language> languages;

    @OneToMany(mappedBy = "cv", cascade = CascadeType.ALL)
    private List<MilitaryExperience> militaryExperience;
}
