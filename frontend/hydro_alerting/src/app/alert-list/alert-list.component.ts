import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { CommonModule, } from '@angular/common';
import {MatTableModule} from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { Router } from '@angular/router';
import { Alert } from '../types/alert';
import { AlertsService } from '../services/alerts.service';
import { Observable, map, tap, filter, mergeMap, of} from 'rxjs';
import { OidcSecurityService, OpenIdConfiguration } from 'angular-auth-oidc-client';


import { ReactiveFormsModule, FormsModule } from '@angular/forms';


@Component({
  selector: 'app-alert-list',
  standalone: true,
  imports: [
    ReactiveFormsModule, 
    FormsModule, 
    CommonModule, 
    MatTableModule, 
    MatButtonModule],
  templateUrl: './alert-list.component.html',
  styleUrl: './alert-list.component.css'
})
export class AlertListComponent implements OnInit{
  displayedColumns: string[] = ['alert_id', 'alert_description', 'last_updated_time', 'actions'];
  alerts!: Observable<Alert[]>;

  // used to keep track if session has been authenticated
  authenticated: boolean = false;

  constructor(
    private router: Router, 
    private alertService: AlertsService,
    private oidcSecurityService: OidcSecurityService) { }


  // view() {
  //   console.log("view alert clicked");
  // }

  view_alert(row: any) {
    console.log(`edit alert clicked: ${JSON.stringify(row)}`);
    // this.selected_alert.emit(row.alert_id);
    this.router.navigate(['/alert', row.alert_id]);
  }

  create_alert() {
    console.log("create alert clicked");
    this.router.navigate(['/alert/create']);
  }



  ngOnInit(): void {
    // this.alerts = this.alertService.getAlerts();
    // configuration$: Observable<OpenIdConfiguration>;
  

    this.oidcSecurityService.isAuthenticated$.subscribe((isAuthenticated) => {
      console.log("is authenticated", isAuthenticated.isAuthenticated);
      this.authenticated = isAuthenticated.isAuthenticated;
    });


    this.alerts = this.alertService.getAlerts().pipe(map((alerts) => {
      return alerts.map((alert) => {
        // alert.streak = alert.id <= 2 ? true : false;
        console.log("alert: " + JSON.stringify(alert));
        return alert;
      });
    }));



  }
}
