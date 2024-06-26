import { Injectable } from '@angular/core';
import { Observable, catchError, of, switchMap, throwError } from 'rxjs';
import { HttpClient } from '@angular/common/http';
import { Alert, AlertCreate } from '../types/alert';


@Injectable({
  providedIn: 'root'
})
export class AlertsService {
  alerts: Alert[] = [];

  constructor(private http: HttpClient) { }


  getAlert(id: number): Observable<Alert> {
    let url = `/api/v1/alerts/${id}`;

    return this.http.get<any>(url);
  }

  getAlerts(): Observable<Alert[]> {
    let url = "/api/v1/alerts/";

    return this.http.get<any>(url);
  }

  // todo: define a type for the alertData
  addAlert(alertData: AlertCreate) :Observable<any> {
    console.log('alert data has been submitted', alertData);
    let url = "/api/v1/alerts/";
    return this.http.post<AlertCreate>(url, alertData);
   }

   editAlert(alertData: AlertCreate, alert_id: number) :Observable<any> {
    console.log('alert data has been submitted', alertData);
    let url = "/api/v1/alerts/" + alert_id + "/";
    return this.http.patch<AlertCreate>(url, alertData);
   }

}
