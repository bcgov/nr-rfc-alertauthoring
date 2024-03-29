import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {NavbarComponent} from './navbar/navbar.component';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
// import { Observable } from 'rxjs';
// import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
// import { ReactiveFormsModule } from '@angular/forms';



// import { BasinListComponent } from './basin-list/basin-list.component';

@Component({
    selector: 'app-root',
    standalone: true,
    template: 
    `
    <app-navbar></app-navbar>
    <br><br>
    <router-outlet></router-outlet>
   `,
    styles: ['h1 { color: blue; }'],
    imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, NavbarComponent]
})
export class AppComponent  implements OnInit{
  title = 'Hydrological Alert Authoring System (HAAS)';
  isAuthenticated = false;
  
  constructor(private oidcSecurityService: OidcSecurityService) { }

  logout() {
    this.oidcSecurityService.logoff();
  }

  ngOnInit(): void {}

  get_title() {
    return this.title;
  }



}
