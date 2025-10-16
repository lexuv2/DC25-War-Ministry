import { Routes } from '@angular/router';
import { HrHomeComponent } from './hr-home/hr-home.component';
import { CvListComponent } from './cv-list/cv-list.component';
import { CvDetailsComponent } from './cv-details/cv-details.component';

export const routes: Routes = [
    {path: '', component: HrHomeComponent},
    {path: 'cv', component: CvListComponent},
    {path: 'cv/:id', component: CvDetailsComponent},
    {path: '**', redirectTo: ''}
];
