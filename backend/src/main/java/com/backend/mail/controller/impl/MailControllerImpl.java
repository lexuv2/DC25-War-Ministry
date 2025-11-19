package com.backend.mail.controller.impl;

import com.backend.mail.controller.api.MailController;
import com.backend.Gmail.PutMailRequest;
import com.backend.mail.service.api.MailService;
import com.backend.shared.ApplicationMessage;
import com.backend.shared.ApplicationResponseHandler;
import com.backend.shared.EndpointConstants;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping(EndpointConstants.MAILS)
public class MailControllerImpl implements MailController {

    private final MailService mailService;

    @Autowired
    public MailControllerImpl(MailService mailService) {
        this.mailService = mailService;
    }

    @Override
    public ResponseEntity<Object> create(PutMailRequest mailRequest) {
        return ApplicationResponseHandler.generateResponse(
                ApplicationMessage.MAIL_CREATED,
                HttpStatus.CREATED,
                mailService.create(mailRequest)
        );
    }

    @Override
    public ResponseEntity<Object> getById(UUID id) {
        return ApplicationResponseHandler.generateResponse(
                ApplicationMessage.MAIL_FOUND,
                HttpStatus.OK,
                mailService.findById(id)
        );
    }

    @Override
    public ResponseEntity<Object> getAll() {
        return ApplicationResponseHandler.generateResponse(
                ApplicationMessage.MAIL_FOUND,
                HttpStatus.OK,
                mailService.findAll()
        );
    }

    @Override
    public ResponseEntity<Object> update(PutMailRequest mailRequest, UUID id) {
        return ApplicationResponseHandler.generateResponse(
                ApplicationMessage.MAIL_UPDATED,
                HttpStatus.OK,
                mailService.update(mailRequest, id)
        );
    }

    @Override
    public ResponseEntity<Object> delete(UUID id) {
        mailService.delete(id);
        return ApplicationResponseHandler.generateResponse(
                ApplicationMessage.MAIL_DELETED,
                HttpStatus.OK,
                null
        );
    }
}
