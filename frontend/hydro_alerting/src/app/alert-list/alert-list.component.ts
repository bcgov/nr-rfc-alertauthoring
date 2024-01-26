import { Component } from '@angular/core';
import { CommonModule, } from '@angular/common';
import {MatTableModule} from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { Router } from '@angular/router';


import { ReactiveFormsModule, FormsModule } from '@angular/forms';


export interface AlertElement {
  alert_id: number;
  alert_description: string;
  last_updated_time: Date;
}



@Component({
  selector: 'app-alert-list',
  standalone: true,
  imports: [ReactiveFormsModule, FormsModule, CommonModule, MatTableModule, MatButtonModule],
  templateUrl: './alert-list.component.html',
  styleUrl: './alert-list.component.css'
})
export class AlertListComponent {
  displayedColumns: string[] = ['alert_id', 'alert_description', 'last_updated_time', 'actions'];
  alerts: AlertElement[] = [
    {
      "alert_id": 1,
      "alert_description": 'this is ALSO an alert',
      "last_updated_time": new Date(2018, 0O5, 0O5, 17, 23, 42, 11),
    }, 
    {
      "alert_id": 2,
      "alert_description": 'this is an alert',
      "last_updated_time": new Date(2018, 0O5, 0O5, 17, 23, 42, 11)
    }, 
  ]

  constructor(private router: Router) { }


  view() {
    console.log("view alert clicked");
  }

  view_alert(row: any) {
    console.log(`edit alert clicked: ${JSON.stringify(row)}`);
    this.router.navigate(['/alert', row.alert_id]);

  }

  create_alert() {
    console.log("create alert clicked");
    this.router.navigate(['/create_alert']);
  }

}
