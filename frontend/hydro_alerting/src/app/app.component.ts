import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import {   
  OidcSecurityService,
 } from 'angular-auth-oidc-client';
 import { Observable } from 'rxjs';



import { BasinListComponent } from './basin-list/basin-list.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, BasinListComponent, ReactiveFormsModule],
  // templateUrl: './app.component.html',
  // template: `
  //   <div class="container">
  //   <h1>{{title}}</h1>
  //   <app-basin-list></app-basin-list>
  //   </div>
  // `,
  template: `
    <router-outlet></router-outlet>
  `,

  // styleUrl: './app.component.css'
  styles: ['h1 { color: blue; }']
})
export class AppComponent  implements OnInit {
  title = 'Hydrological Alert Authoring System (HAAS)';
  isAuthenticated = false;

  constructor(public oidcSecurityService: OidcSecurityService) {
  }

  ngOnInit() {
    this.oidcSecurityService
      .checkAuth()
      .subscribe(({ isAuthenticated, userData, accessToken, idToken, configId}) => {
        console.log('app authenticated', isAuthenticated);
        console.log('userData', userData);
        console.log(`Current access token is '${accessToken}'`);
        console.log(`idToken '${idToken}'`);
        console.log(`configId '${configId}'`);

  });
}

}
