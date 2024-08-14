import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import {HeaderComponent} from './header/header.component';
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
    <div class="header-locked">
        <app-header></app-header>
        <app-navbar></app-navbar>
    </div>
    
    <div class="content-container">
        <router-outlet></router-outlet>
    </div>
   `,
    styles: [`h1 { color: blue; } 
            .header-locked { position: sticky; position: -webkit-sticky; top:168px; z-index: 10000;} 
            .content-container {
              position: absolute;
              top: 168px; /* Adjust based on the height of your toolbar */
              bottom: 0;
              left: 0;
              right: 0;
              overflow-y: auto; /* Enable vertical scrolling */
              padding: 20px; /* Optional: Add padding for better appearance */
      }
`],
    imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, NavbarComponent, HeaderComponent]
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
