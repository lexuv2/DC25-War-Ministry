package com.backend.cv.service.api;

import com.backend.cv.dto.PutCVRequest;
import com.backend.cv.entity.CV;
import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import org.springframework.validation.annotation.Validated;

import java.util.List;
import java.util.UUID;

@Validated
public interface CVService {

    CV create(@Valid PutCVRequest cvRequest);

    List<CV> findAll();

    CV findById(@NotNull UUID id);

    CV update(@Valid PutCVRequest cvRequest, @NotNull UUID id);

    void delete(@NotNull UUID id);

    boolean existsById(@NotNull UUID id);
}
