import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { CvTableItem } from '../cv-table/cv-table-datasource';
import { CvDetails } from '../cv-details/cv-details.component';

@Injectable({
  providedIn: 'root'
})
export class CvService {

  constructor(private http: HttpClient) {}

  getCvList() {
    var cvList = this.http.get<CvTableItem[]>('http://localhost:8080/cv');
    return cvList;
  }

  getCv(id: string) {
    var cv = this.http.get<CvDetails>(`http://localhost:8080/cv/${id}`);
    return cv;
  }
}
