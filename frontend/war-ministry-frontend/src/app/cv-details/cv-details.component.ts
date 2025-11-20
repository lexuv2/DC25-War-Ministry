import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatIconModule } from '@angular/material/icon';
import { MatList, MatListModule } from '@angular/material/list';
import { MatMenuModule } from '@angular/material/menu';
import { ActivatedRoute } from '@angular/router';
import { CvService } from '../cv/cv.service';
import { BehaviorSubject, catchError, of } from 'rxjs';
import { NgFor } from '@angular/common';

export interface CvDetails {
  id: string;
  fullName: string;
  dateOfBirth: string;
  nationality: string;
  email: string;
  phone: string;
  address: string;

  education: EducationDetails[];
  workExperience: WorkExperienceDetails[];
  skills: string[];
  certifications: CertificationDetails[];
  languages: LanguageDetails[];
  militaryExperience: MilitaryExperienceDetails[];

  score: number;
}

export interface EducationDetails {
  id: string;
  degree: string;
  institution: string;
  startDate: string;
  endDate: string;
  fieldOfStudy: string;
  cv: string;
}

export interface WorkExperienceDetails {
  id: string;
  jobTitle: string;
  company: string;
  startDate: string;
  endDate: string;
  cv: string; 
}

export interface CertificationDetails {
  id: string;
  name: string;
  issuingOrganization: string;
  cv: string;
}

export interface LanguageDetails {
  id: string;
  language: string;
  proficiency: string;
  cv: string;
}

export interface MilitaryExperienceDetails {
  id: string;
  rank: string;
  branch: string;
  startDate: string;
  endDate: string;
  duties: string[];
  cv: string;
}

@Component({
  selector: 'app-cv-details',
  imports: [MatExpansionModule,
    MatMenuModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    MatGridListModule,
    MatListModule,
    MatChipsModule,
    NgFor],
  templateUrl: './cv-details.component.html',
  styleUrl: './cv-details.component.scss'
})
export class CvDetailsComponent {
  cv! : CvDetails;
  error$ = new BehaviorSubject<string | null>(null);

  constructor(
    private route: ActivatedRoute,
    private cvService: CvService
  ) {}

  ngOnInit(): void {
    const id = this.route.snapshot.paramMap.get('id')!;

    this.cvService.getCv(id)
      .pipe(
        catchError(err => {
          this.error$.next('Błąd pobierania CV, spróbuj ponownie później.');
          return of(null);
        })
      )
      .subscribe((data) => {
        if (data) {
          this.cv = data;
          this.error$.next(null);
        }
      });
  }
}
