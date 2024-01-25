import { Component } from '@angular/core';
import { CommonModule, } from '@angular/common';
import {MatTableModule} from '@angular/material/table';


import { ReactiveFormsModule, FormsModule } from '@angular/forms';


export interface AlertElement {
  alert_id: number;
  alert_description: string;
  start_time: Date;
}



@Component({
  selector: 'app-alert-list',
  standalone: true,
  imports: [ReactiveFormsModule, FormsModule, CommonModule, MatTableModule],
  templateUrl: './alert-list.component.html',
  styleUrl: './alert-list.component.css'
})
export class AlertListComponent {
  alerts: AlertElement[] = [
    {
      "alert_id": 1,
      "alert_description": 'this is ALSO an alert',
      "start_time": new Date(2018, 0O5, 0O5, 17, 23, 42, 11)
    }, 
    {
      "alert_id": 2,
      "alert_description": 'this is an alert',
      "start_time": new Date(2018, 0O5, 0O5, 17, 23, 42, 11)
    }, 
  ]
  view() {
    console.log("view alert clicked");
  }

}
