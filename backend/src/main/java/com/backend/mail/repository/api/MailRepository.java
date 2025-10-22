package com.backend.mail.repository.api;

import com.backend.mail.entity.Mail;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface MailRepository extends JpaRepository<Mail, UUID> {
}
