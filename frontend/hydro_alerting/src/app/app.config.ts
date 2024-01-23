
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import {APP_INITIALIZER, ApplicationConfig } from '@angular/core';
import {
  provideRouter
} from '@angular/router';
import { AuthConfig, provideOAuthClient, OAuthService } from 'angular-oauth2-oidc';
import { routes } from './app.routes';



export const authCodeFlowConfig: AuthConfig = {
  issuer: 'https://dev.loginproxy.gov.bc.ca/auth/realms/standard',
  tokenEndpoint: 'https://dev.loginproxy.gov.bc.ca/auth/realms/standard/protocol/openid-connect/token',
  // redirectUri: window.location.origin + '/index.html',
  redirectUri: window.location.origin,
  clientId: 'hydrological-alerting-5261',
  responseType: 'code',
  // scope: 'openid profile email offline_access',
  scope: 'openid profile email offline_access',
  showDebugInformation: true,
  requireHttps: false,
  oidc: true,
  disablePKCE: false
}



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
