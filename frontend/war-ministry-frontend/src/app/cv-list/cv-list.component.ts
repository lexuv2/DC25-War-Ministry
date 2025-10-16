import { Component } from '@angular/core';
import { CvTableComponent } from '../cv-table/cv-table.component';

@Component({
  selector: 'app-cv-list',
  imports: [CvTableComponent],
  templateUrl: './cv-list.component.html',
  styleUrl: './cv-list.component.scss'
})
export class CvListComponent {

}
