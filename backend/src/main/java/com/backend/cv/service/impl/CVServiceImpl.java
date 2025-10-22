package com.backend.cv.service.impl;


import com.backend.cv.dto.PutCVRequest;
import com.backend.cv.entity.CV;
import com.backend.cv.function.RequestToCVFunction;
import com.backend.cv.repository.api.CVRepository;
import com.backend.cv.service.api.CVService;
import com.backend.shared.ApplicationError;
import com.backend.shared.ApplicationMessage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.UUID;

@Service
public class CVServiceImpl implements CVService {

    private final CVRepository cvRepository;

    private final RequestToCVFunction requestToCVFunction;

    @Autowired
    public CVServiceImpl(CVRepository cvRepository, RequestToCVFunction requestToCVFunction) {
        this.cvRepository = cvRepository;
        this.requestToCVFunction = requestToCVFunction;
    }

    @Override
    public CV create(PutCVRequest cvRequest) {
        return cvRepository.save(
                requestToCVFunction.apply(cvRequest)
        );
    }

    @Override
    public List<CV> findAll() {
        return cvRepository.findAll();
    }

    @Override
    public CV findById(UUID id) {
        return cvRepository.findById(id).orElseThrow(() -> new ApplicationError(HttpStatus.NOT_FOUND, ApplicationMessage.CV_NOT_FOUND));
    }

    @Override
    public CV update(PutCVRequest cvRequest, UUID id) {
        existsByIdOrThrowException(id);

        return cvRepository.save(
                requestToCVFunction.apply(cvRequest, id)
        );
    }

    @Override
    public void delete(UUID id) {
        existsByIdOrThrowException(id);
        cvRepository.deleteById(id);
    }

    @Override
    public boolean existsById(UUID id) {
        return cvRepository.existsById(id);
    }

    private void existsByIdOrThrowException(UUID id) {
        if (!existsById(id)) {
            throw new ApplicationError(HttpStatus.NOT_FOUND, ApplicationMessage.CV_NOT_FOUND);
        }
    }
}
