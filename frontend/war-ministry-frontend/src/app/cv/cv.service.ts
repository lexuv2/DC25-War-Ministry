import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { CvTableItem } from '../cv-table/cv-table-datasource';
import { catchError, of } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class CvService {

  constructor(private http: HttpClient) {}

  getCvList() {
  return this.http.get<CvTableItem[]>('http://localhost:8080/cv').pipe(
    catchError(() => {
      return of([]);
    })
  );
}
}
