import { Injectable } from '@angular/core';
import { Observable, of } from 'rxjs';
import { Basin } from '../types/basin';
import { HttpClientModule } from '@angular/common/http';
import { HttpClient } from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class BasinService {
  basins: Basin[] = [
    {
      id: 1,
      basin_name: 'basin 1'
    },
    {
      id: 2,
      basin_name: 'basin 2'
    },
    {
      id: 3,
      basin_name: 'basin 33'
    },
    {
      id: 4,
      basin_name: 'silly basin'
    }
  ];
// 
  constructor(private http: HttpClient ) { }

  getBasins(): Observable<Basin[]> {

    //return of(this.basins);

    // let url = "http://localhost:3003/api/v1/basins";
    let url = "/api/v1/basins/";
    // let data = this.http.get<Basin[]>(url);
    // console.log("data: " + JSON.stringify(data));
    return this.http.get<Basin[]>(url);
  }

  addBasin(basinData: any) {
    console.log('Your basin has been submitted', basinData);
    const basin_id = this.basins.length + 1;
    basinData.id = basin_id;
    basinData.streak = false;

    this.basins.push(basinData);
    console.log("basins: " + JSON.stringify(this.basins));
   }

}
