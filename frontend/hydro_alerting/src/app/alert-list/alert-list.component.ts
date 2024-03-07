import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { CommonModule, } from '@angular/common';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { Router } from '@angular/router';
import { Alert } from '../types/alert';
import { AlertsService } from '../services/alerts.service';
import { Observable, map} from 'rxjs';
import { OidcSecurityService, OpenIdConfiguration } from 'angular-auth-oidc-client';

import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import {AuthzService} from '../services/authz.service';


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
export class AlertListComponent implements OnInit {
  displayedColumns: string[] = ['alert_id', 'alert_description', 'last_updated_time', 'actions'];
  alerts!: Observable<Alert[]>;

  // used to keep track if session has been authenticated
  is_authorized: boolean = false;

  constructor(
    private router: Router,
    private alertService: AlertsService,
    private oidcSecurityService: OidcSecurityService, 
    private authzService: AuthzService
    ) { }

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

    this.authzService.canEdit().subscribe((authData) => {
      console.log("GETTING DATA FROM SERVICE: " + JSON.stringify(authData));
      this.is_authorized = authData;
    });


    // this.oidcSecurityService.isAuthenticated$.pipe(
    //   concatMap((isAuthenticated) => {
    //     this.authenticated = isAuthenticated.isAuthenticated;
    //     if (isAuthenticated.isAuthenticated) {
    //       // if we are authenticated then get the payload so we can 
    //       // evalute authorization          
    //       return this.oidcSecurityService.getPayloadFromAccessToken();
    //     } else {
    //       // not authenticated so return empty, which has no effect on the downstream subscription
    //       return EMPTY;
    //     }
    //   })).subscribe((payload) => {
    //     console.log(`ZZZ is authenticated3 ${payload}`);
    //     if (payload.client_roles) {
    //       this.auth_roles = payload.client_roles;
    //     }
    //   });

    // todo: this logic can get wrapped in a service
    this.alerts = this.alertService.getAlerts().pipe(map((alerts) => {
      return alerts.map((alert) => {
        // alert.streak = alert.id <= 2 ? true : false;
        console.log("alert: " + JSON.stringify(alert));
        return alert;
      });
    }));
  }
}
