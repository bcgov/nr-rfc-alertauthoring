// import { AuthConfig } from 'angular-oauth2-oidc';
import {OpenIdConfiguration, LogLevel } from 'angular-auth-oidc-client';

export const authCodeFlowConfig: OpenIdConfiguration = {
    authority: 'https://dev.loginproxy.gov.bc.ca/auth/realms/standard',
    // redirectUri: window.location.origin + '/index.html',
    redirectUrl: window.location.origin,
    // redirectUrl: 'http://localhost:4200',
    postLogoutRedirectUri: window.location.origin,

    clientId: 'hydrological-alerting-5261',
    responseType: 'code',
    // offline_access - don't use
    scope: 'openid profile email',
    // silentRenew: true,
    useRefreshToken: true,
    logLevel: LogLevel.Debug,
}
