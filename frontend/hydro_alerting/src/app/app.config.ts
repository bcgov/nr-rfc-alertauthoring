
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import {APP_INITIALIZER, ApplicationConfig } from '@angular/core';
import {
  provideRouter
} from '@angular/router';
import { provideAuth, authInterceptor } from 'angular-auth-oidc-client';
import { routes } from './app.routes';
import { authCodeFlowConfig } from './sso.config';
import { provideAnimations } from '@angular/platform-browser/animations';
import { provideQuillConfig } from 'ngx-quill/config';

export const appConfig: ApplicationConfig = {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor()])),
    provideAuth({
      config: 
        authCodeFlowConfig
    }),
    provideAnimations(),
    provideQuillConfig({
        customOptions: [{
        import: 'formats/font',
        whitelist: ['mirza', 'roboto', 'aref', 'serif', 'sansserif', 'monospace']
      }]
    })

  ]
};
