
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import {APP_INITIALIZER, ApplicationConfig } from '@angular/core';
import {
  provideRouter
} from '@angular/router';
import { AuthConfig, provideOAuthClient, OAuthService } from 'angular-oauth2-oidc';
import { routes } from './app.routes';
import { authCodeFlowConfig } from './sso.config';


function initializeOAuth(oauthService: OAuthService): Promise<void> {
  return new Promise((resolve) => {
    oauthService.configure(authCodeFlowConfig);
    oauthService.setupAutomaticSilentRefresh();
    oauthService.loadDiscoveryDocumentAndLogin()
      .then(() => resolve());
  }
  );
}

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(),
    provideOAuthClient(),
    {
      provide: APP_INITIALIZER,
      useFactory: (oauthService: OAuthService) => {
        return () => {
          initializeOAuth(oauthService);
        }
      },
      multi: true,
      deps: [
        OAuthService
      ]
    }
  ]
};
// https://dev.loginproxy.gov.bc.ca/auth/realms/standard/.well-known/openid-configuration