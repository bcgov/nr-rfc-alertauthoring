import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';

import {
  OidcClientNotification,
  OidcSecurityService,
  OpenIdConfiguration,
  UserDataResult,
  
} from 'angular-auth-oidc-client';
import { Observable } from 'rxjs';


@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './home.component.html',
  styleUrl: './home.component.css'
})
export class HomeComponent {
  configuration$: Observable<OpenIdConfiguration> | undefined;
  userDataChanged$: Observable<OidcClientNotification<any>> | undefined;
  userData$: Observable<UserDataResult> | undefined;
  isAuthenticated = false;
  constructor(public oidcSecurityService: OidcSecurityService) {}

  ngOnInit() {
    this.configuration$ = this.oidcSecurityService.getConfiguration();
    this.userData$ = this.oidcSecurityService.userData$;

    this.oidcSecurityService.isAuthenticated$.subscribe(
      ({ isAuthenticated }) => {
        this.isAuthenticated = isAuthenticated;

        console.warn('authenticated: ', isAuthenticated);
      }
    );
  }

  login() {
    this.oidcSecurityService.authorize();
  }

  refreshSession() {
    this.oidcSecurityService
      .forceRefreshSession()
      .subscribe((result) => console.log(result));
  }

  logout() {
    this.oidcSecurityService
      .logoff()
      .subscribe((result) => console.log(result));
  }

  logoffAndRevokeTokens() {
    this.oidcSecurityService
      .logoffAndRevokeTokens()
      .subscribe((result) => console.log(result));
  }

  revokeRefreshToken() {
    this.oidcSecurityService
      .revokeRefreshToken()
      .subscribe((result) => console.log(result));
  }

  revokeAccessToken() {
    this.oidcSecurityService
      .revokeAccessToken()
      .subscribe((result) => console.log(result));
  }


}
