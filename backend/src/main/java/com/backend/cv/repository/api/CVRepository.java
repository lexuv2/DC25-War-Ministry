package com.backend.cv.repository.api;

import com.backend.cv.entity.CV;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.UUID;

public interface CVRepository extends JpaRepository<CV, UUID> {
}
