import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { Alert } from '../types/alert';


@Injectable({
  providedIn: 'root'
})
export class AlertsService {
  alerts: Alert[] = [];

  constructor(private http: HttpClient) { }

  getAlerts(): Observable<Alert[]> {
    let url = "/api/v1/alerts";

    return this.http.get<any>(url);
  }

  addAlert(alertData: any) {
    console.log('alert data has been submitted', alertData);

    this.alerts.push(alertData);
    // console.log("basins: " + JSON.stringify(this.alerts));
   }
}
