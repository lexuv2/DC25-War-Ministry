package com.backend.helperClasses.entities;

import java.time.LocalDate;
import java.util.List;
import java.util.UUID;

import com.backend.cv.entity.CV;
import jakarta.persistence.*;
import lombok.Getter;
import lombok.Setter;

@Entity
@Getter
@Setter
public class MilitaryExperience {

    @Id
    @GeneratedValue
    private UUID id;

    private String rank;
    private String branch;
    private LocalDate startDate;
    private LocalDate endDate;

    @ElementCollection
    private List<String> duties;

    @ManyToOne
    private CV cv;
}
