package com.backend.cv.service.impl;


import com.backend.cv.dto.CvDto;
import com.backend.cv.dto.PutCVRequest;
import com.backend.cv.entity.CV;
import com.backend.cv.function.RequestToCVFunction;
import com.backend.cv.repository.api.CVRepository;
import com.backend.cv.service.api.CVService;
import com.backend.helperClasses.dtos.ContactDto;
import com.backend.helperClasses.entities.*;
import com.backend.shared.ApplicationError;
import com.backend.shared.ApplicationMessage;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import java.util.Comparator;
import java.util.List;
import java.util.Random;
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
    public List<CV> findAllAndSort() {
        List<CV> cvs = cvRepository.findAll();
        cvs.sort(Comparator.comparing(CV::getScore).reversed());
        return cvs;
    }

    @Override
    public CV findById(UUID id) {
        return cvRepository.findById(id).orElseThrow(() -> new ApplicationError(HttpStatus.NOT_FOUND, ApplicationMessage.CV_NOT_FOUND));
    }

    @Override
    public CV processCV(CvDto dto) {
        CV cv = new CV();
        cv.setFullName(dto.getPersonalInfo().getFullName());
        cv.setDateOfBirth(dto.getPersonalInfo().getDateOfBirth());
        cv.setNationality(dto.getPersonalInfo().getNationality());

        ContactDto contact = dto.getPersonalInfo().getContact();
        cv.setEmail(contact.getEmail());
        cv.setPhone(contact.getPhone());
        cv.setAddress(contact.getAddress());

        // EDUCATION
        List<Education> eduList = dto.getEducation().stream()
                .map(e -> {
                    Education ed = new Education();
                    ed.setDegree(e.getDegree());
                    ed.setInstitution(e.getInstitution());
                    ed.setStartDate(e.getStartDate());
                    ed.setEndDate(e.getEndDate());
                    ed.setFieldOfStudy(e.getFieldOfStudy());
                    ed.setCv(cv);
                    return ed;
                }).toList();
        cv.setEducation(eduList);

        // WORK EXPERIENCE
        List<WorkExperience> weList = dto.getWorkExperience().stream()
                .map(w -> {
                    WorkExperience we = new WorkExperience();
                    we.setJobTitle(w.getJobTitle());
                    we.setCompany(w.getCompany());
                    we.setStartDate(w.getStartDate());
                    we.setEndDate(w.getEndDate());
                    we.setCv(cv);
                    return we;
                }).toList();
        cv.setWorkExperience(weList);

        // SKILLS
        cv.setSkills(dto.getSkills());

        // CERTIFICATIONS
        cv.setCertifications(
                dto.getCertifications().stream()
                        .map(cert -> {
                            Certification ce = new Certification();
                            ce.setName(cert.getName());
                            ce.setIssuingOrganization(cert.getIssuingOrganization());
                            ce.setCv(cv);
                            return ce;
                        })
                        .toList()
        );

        // LANGUAGES
        cv.setLanguages(
                dto.getLanguages().stream()
                        .map(l -> {
                            Language lang = new Language();
                            lang.setLanguage(l.getLanguage());
                            lang.setProficiency(l.getProficiency());
                            lang.setCv(cv);
                            return lang;
                        })
                        .toList()
        );

        // MILITARY EXPERIENCE
        cv.setMilitaryExperience(
                dto.getMilitaryExperience().stream()
                        .map(me -> {
                            MilitaryExperience e = new MilitaryExperience();
                            e.setRank(me.getRank());
                            e.setBranch(me.getBranch());
                            e.setStartDate(me.getStartDate());
                            e.setEndDate(me.getEndDate());
                            e.setDuties(me.getDuties());
                            e.setCv(cv);
                            return e;
                        })
                        .toList()
        );

        cv.setScore((int)(Math.random() * 100));

        return cvRepository.save(cv);
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
