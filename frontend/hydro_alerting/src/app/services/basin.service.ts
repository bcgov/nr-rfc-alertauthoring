import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { Basin } from '../types/basin';
import { HttpClientModule } from '@angular/common/http';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class BasinService {
 
  constructor(private http: HttpClient ) { }

  getBasins(): Observable<Basin[]> {

    //return of(this.basins);

    // let url = "http://localhost:3003/api/v1/basins";
    let url = "/api/v1/basins/";
    // let data = this.http.get<Basin[]>(url);
    // console.log("data: " + JSON.stringify(data));
    return this.http.get<Basin[]>(url);
  }

}
