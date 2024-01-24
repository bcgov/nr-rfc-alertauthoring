import { AuthConfig } from 'angular-oauth2-oidc';

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
    disablePKCE: false,
    sessionChecksEnabled: true,
  }
  