package com.backend.mail.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.*;

import java.util.UUID;

@Getter
@Setter
@Entity
@NoArgsConstructor
@AllArgsConstructor
@Builder
@Table(name = "mail")
public class Mail {
    //nie wiem co dokladnie bedzie tu potrzebne
    //wiec zostawiam bare bones
    @Id
    private UUID id;

    @Column(nullable = false)
    private String emailAddress;
}
