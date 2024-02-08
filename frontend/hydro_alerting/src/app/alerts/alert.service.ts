import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { Alert } from '../alert';


@Injectable({
  providedIn: 'root'
})
export class AlertService {
  alert!: Alert;

  constructor(private http: HttpClient) { }

  getAlert(id: number): Observable<Alert> {
    let url = `/api/v1/alerts/${id}`;

    return this.http.get<any>(url);
  }
  
}
