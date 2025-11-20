package com.backend.mail.service.api;

import com.backend.Gmail.PutMailRequest;
import com.backend.mail.entity.Mail;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import org.springframework.validation.annotation.Validated;

import java.util.List;
import java.util.UUID;

@Validated
public interface MailService {

    Mail create(@Valid PutMailRequest mailRequest);

    List<Mail> findAll();

    Mail findById(@NotNull UUID id);

    Mail update(@Valid PutMailRequest mailRequest, @NotNull UUID id);

    void delete(@NotNull UUID id);

    boolean existsById(@NotNull UUID id);
}
