package com.backend.cv.function;

import com.backend.cv.dto.PutCVRequest;
import com.backend.cv.entity.CV;
import org.springframework.stereotype.Component;

import java.util.UUID;
import java.util.function.Function;

@Component
public class RequestToCVFunction implements Function<PutCVRequest, CV>{

    @Override
    public CV apply(PutCVRequest cvRequest) {
        return CV.builder()
                .fullName(cvRequest.fullName())
                .email(cvRequest.email())
                .address(cvRequest.address())
                .dateOfBirth(cvRequest.dateOfBirth())
                .nationality(cvRequest.nationality())
                .phone(cvRequest.phone())
                .build();
    }

    public CV apply(PutCVRequest cvRequest, UUID id) {
        CV cv = apply(cvRequest);
        cv.setId(id);
        return cv;
    }
}
