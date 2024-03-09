import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, Router, RouterStateSnapshot, UrlTree } from '@angular/router';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { Observable } from 'rxjs';
import { map, take } from 'rxjs/operators';
import {AuthzService} from '../services/authz.service';
import { environment } from '../../environments/environment';

@Injectable({ providedIn: 'root' })
export class AuthorizationGuard implements CanActivate {
  constructor(
    private oidcSecurityService: OidcSecurityService,
    private authzService: AuthzService,
    private router: Router) {}

  canActivate(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<boolean | UrlTree> {
    return this.authzService.canEdit().pipe(
      map((authData) => {
        console.log(`env data: ${JSON.stringify(environment)}`);
        // allow navigation if authenticated and authorized
        if (authData || environment.disable_route_guard) {
          return true;
        }
        // redirect if not authenticated
        return this.router.parseUrl('/unauthorized');
      })
    );
  }
}


