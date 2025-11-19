package com.backend.mail.function;

import com.backend.Gmail.PutMailRequest;
import com.backend.mail.entity.Mail;
import org.springframework.stereotype.Component;

import java.util.UUID;
import java.util.function.Function;

@Component
public class RequestToMailFunction implements Function<PutMailRequest, Mail>{

    @Override
    public Mail apply(PutMailRequest mailRequest) {
        return Mail.builder()
                .emailAddress(mailRequest.emailAddress())
                .build();
    }

    public Mail apply(PutMailRequest mailRequest, UUID id) {
        Mail mail = apply(mailRequest);
        mail.setId(id);
        return mail;
    }
}
