package com.backend.helperClasses.entities;

import java.time.LocalDate;
import java.util.UUID;

import com.backend.cv.entity.CV;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import jakarta.persistence.ManyToOne;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
public class WorkExperience {

    @Id
    @GeneratedValue
    private UUID id;

    private String jobTitle;
    private String company;
    private LocalDate startDate;
    private LocalDate endDate;

    @ManyToOne
    private CV cv;
}
