package com.backend.Gmail;

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
@Table(name = "gmail")
public class GmailEntity {
    @Id
    private int messageId;

    @Column(nullable = false)
    private String emailAddress;

    private Boolean wasHandled;
}
