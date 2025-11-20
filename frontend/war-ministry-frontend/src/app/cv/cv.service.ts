import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { CvTableItem } from '../cv-table/cv-table-datasource';
import { CvDetails } from '../cv-details/cv-details.component';
import { map } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CvService {

  constructor(private http: HttpClient) {}

  getCvList() {
    return this.http.get<{data: CvTableItem[]}>('http://localhost:8080/cv')
      .pipe(map(res => res.data));
  }


  getCv(id: string) {
    return this.http.get<{data: CvDetails}>(`http://localhost:8080/cv/${id}`)
      .pipe(map(res => res.data));
  }
}
