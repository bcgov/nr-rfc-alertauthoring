import { ApplicationConfig, importProvidersFrom } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { AuthModule, LogLevel } from 'angular-auth-oidc-client';


import { routes } from './app.routes';

// scope: offline_access
export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes), 
    provideHttpClient(),
    importProvidersFrom(AuthModule.forRoot({
      config: {
        authority: 'https://dev.loginproxy.gov.bc.ca/auth/realms/standard',
        redirectUrl: window.location.origin,
        postLogoutRedirectUri: window.location.origin,
        clientId: 'hydrological-alerting-5260',
        scope: 'openid idir email profile',
        responseType: 'code',
        silentRenew: true,
        useRefreshToken: true,
        logLevel: LogLevel.Debug,
      },
    }))
]
};
// https://dev.loginproxy.gov.bc.ca/auth/realms/standard/.well-known/openid-configuration