import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpInterceptorFn, HttpHandlerFn } from '@angular/common/http';
import { Observable, switchMap } from 'rxjs';
import { AuthzService } from '../services/authz.service';
// import 

@Injectable()
export class AlertsWriteInterceptor implements HttpInterceptor {
  // These are the routes that are going to be monitored for.
  private secureRoutes = ['/api/v1/alerts', '/api/v1/alerts/*'];

  constructor(private authzService: AuthzService) {
    console.log("interceptor has been created")
  }

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    console.log("interceptor request")
    console.log(`request: ${JSON.stringify(request)}`)
    if ((request.method === 'POST' || request.method === 'PUT' || request.method === 'PATCH' ||  request.method === 'DELETE') && this.isSecureRoute(request.url)) {
      return this.authzService.getToken().pipe(
        switchMap((token) => {
          if (token) {
            console.log("got token", token)
            request = request.clone({
              setHeaders: {
                Authorization: `Bearer ${token}`
              }
            });
          }
          // console.log("returning next.handle(request)")
          return next.handle(request);
        })
      );
      }
    else {
      return next.handle(request);
    }
  }

  private isSecureRoute(url: string): boolean {
    return this.secureRoutes.some(route => url.startsWith(route));
  }
}


// export const noopInterceptor: HttpInterceptorFn = (req: HttpRequest<unknown>, next:
//   HttpHandlerFn) => {
//     console.log("interceptor request")
//     return next(req);
//   };
  