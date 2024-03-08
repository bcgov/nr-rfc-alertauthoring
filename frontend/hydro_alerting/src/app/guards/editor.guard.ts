import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { Observable } from 'rxjs';
import { map, take } from 'rxjs/operators';
import {AuthzService} from '../services/authz.service';

@Injectable({ providedIn: 'root' })
export class AuthorizationGuard implements CanActivate {
  constructor(
    private oidcSecurityService: OidcSecurityService,
    private authzService: AuthzService,
    private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean | UrlTree> {
    return this.authzService.canEdit().pipe(
      map((authData) => {
        // allow navigation if authenticated
        if (authData) {
          return true;
        }
        // redirect if not authenticated
        return this.router.parseUrl('/unauthorized');
      })
    );
  }
}


