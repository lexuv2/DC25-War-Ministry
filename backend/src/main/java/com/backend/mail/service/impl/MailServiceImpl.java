package com.backend.mail.service.impl;


import com.backend.mail.repository.api.MailRepository;
import com.backend.mail.dto.PutMailRequest;
import com.backend.mail.entity.Mail;
import com.backend.mail.function.RequestToMailFunction;
import com.backend.mail.service.api.MailService;
import com.backend.shared.ApplicationError;
import com.backend.shared.ApplicationMessage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
public class MailServiceImpl implements MailService {

    private final MailRepository mailRepository;

    private final RequestToMailFunction requestToMailFunction;

    @Autowired
    public MailServiceImpl(MailRepository mailRepository, RequestToMailFunction requestToMailFunction) {
        this.mailRepository = mailRepository;
        this.requestToMailFunction = requestToMailFunction;
    }

    @Override
    public Mail create(PutMailRequest mailRequest) {
        return mailRepository.save(
                requestToMailFunction.apply(mailRequest)
        );
    }

    @Override
    public List<Mail> findAll() {
        return mailRepository.findAll();
    }

    @Override
    public Mail findById(UUID id) {
        return mailRepository.findById(id).orElseThrow(() -> new ApplicationError(HttpStatus.NOT_FOUND, ApplicationMessage.MAIL_NOT_FOUND));
    }

    @Override
    public Mail update(PutMailRequest cvRequest, UUID id) {
        existsByIdOrThrowException(id);

        return mailRepository.save(
                requestToMailFunction.apply(cvRequest, id)
        );
    }

    @Override
    public void delete(UUID id) {
        existsByIdOrThrowException(id);
        mailRepository.deleteById(id);
    }

    @Override
    public boolean existsById(UUID id) {
        return mailRepository.existsById(id);
    }

    private void existsByIdOrThrowException(UUID id) {
        if (!existsById(id)) {
            throw new ApplicationError(HttpStatus.NOT_FOUND, ApplicationMessage.MAIL_NOT_FOUND);
        }
    }
}
