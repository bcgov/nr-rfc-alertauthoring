import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { AlertLevel } from '../types/alert';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AlertLvlsService {

  constructor(private http: HttpClient ) { }

  getAlertLvls(): Observable<AlertLevel[]> {
    let url = "/api/v1/alert_levels/";
    return this.http.get<AlertLevel[]>(url);
  }

}
