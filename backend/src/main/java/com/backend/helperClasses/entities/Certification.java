package com.backend.helperClasses.entities;

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
public class Certification {

    @Id
    @GeneratedValue
    private UUID id;

    private String name;
    private String issuingOrganization;

    @ManyToOne
    private CV cv;
}
