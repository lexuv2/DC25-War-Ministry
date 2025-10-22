package com.backend.cv.controller.impl;

import com.backend.cv.controller.api.CVController;
import com.backend.cv.dto.PutCVRequest;
import com.backend.cv.service.api.CVService;
import com.backend.shared.ApplicationResponseHandler;
import com.backend.shared.ApplicationMessage;
import com.backend.shared.EndpointConstants;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping(EndpointConstants.CV)
public class CVControllerImpl implements CVController {

    private final CVService cvService;

    @Autowired
    public CVControllerImpl(CVService cvService) {
        this.cvService = cvService;
    }

    @Override
    public ResponseEntity<Object> create(PutCVRequest cvRequest) {
        return ApplicationResponseHandler.generateResponse(
                ApplicationMessage.CV_CREATED,
                HttpStatus.CREATED,
                cvService.create(cvRequest)
        );
    }

    @Override
    public ResponseEntity<Object> getById(UUID id) {
        return ApplicationResponseHandler.generateResponse(
                ApplicationMessage.CV_FOUND,
                HttpStatus.OK,
                cvService.findById(id)
        );
    }

    @Override
    public ResponseEntity<Object> getAll() {
        return ApplicationResponseHandler.generateResponse(
                ApplicationMessage.CV_FOUND,
                HttpStatus.OK,
                cvService.findAll()
        );
    }

    @Override
    public ResponseEntity<Object> update(PutCVRequest cvRequest, UUID id) {
        return ApplicationResponseHandler.generateResponse(
                ApplicationMessage.CV_UPDATED,
                HttpStatus.OK,
                cvService.update(cvRequest, id)
        );
    }

    @Override
    public ResponseEntity<Object> delete(UUID id) {
        cvService.delete(id);
        return ApplicationResponseHandler.generateResponse(
                ApplicationMessage.CV_DELETED,
                HttpStatus.OK,
                null
        );
    }
}
