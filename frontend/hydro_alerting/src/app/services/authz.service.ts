import { Injectable } from '@angular/core';
import { environment } from '../../environments/environment';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { concatMap, EMPTY, of } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthzService {
  authenticated = false;
  authorized = false;
  member_roles = [];


  canEdit() {
    return this.oidcSecurityService.isAuthenticated$.pipe(
      concatMap((isAuthenticated) => {
        this.authenticated = isAuthenticated.isAuthenticated;
        if (isAuthenticated.isAuthenticated) {
          // if we are authenticated then get the payload so we can 
          // evalute authorization          
          return this.oidcSecurityService.getPayloadFromAccessToken();
        } else {
          // not authenticated so return empty list of client roles which has no effect on the downstream subscription
          return of({client_roles: []});
        }
      }),
      concatMap((payload) => {
        if (payload.client_roles) {
          this.member_roles = payload.client_roles;
          if (payload.client_roles.includes(environment.roles.editor)) {
            this.authorized = true;
          }
        }
        return of(this.authorized);
      }));
  }





  constructor(private oidcSecurityService: OidcSecurityService) {
    this.oidcSecurityService.isAuthenticated$.pipe(
      concatMap((isAuthenticated) => {
        console.log(`ZZZ is authenticated2 ${isAuthenticated.isAuthenticated}`);
        this.authenticated = isAuthenticated.isAuthenticated;
        if (isAuthenticated.isAuthenticated) {
          // if we are authenticated then get the payload so we can 
          // evalute authorization          
          return this.oidcSecurityService.getPayloadFromAccessToken();
        } else {
          // not authenticated so return empty, which has no effect on the downstream subscription
          return EMPTY;
        }
      })).subscribe((payload) => {
        console.log(`ZZZ is authenticated3 ${payload}`);
        if (payload.client_roles) {
          this.member_roles = payload.client_roles;
          if (environment.roles.editor in this.member_roles) {
            this.authorized = true;
          }
        }
        // todo: define a type for this return type
        // return of({"authorized": this.authorized, "authenticated": this.authenticated});
      });
  }
}
