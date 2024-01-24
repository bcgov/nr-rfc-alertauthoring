import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { OAuthService } from 'angular-oauth2-oidc';
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
    // template: `
    //   <div class="container">
    //   <h1>{{title}}</h1>
    //   <app-basin-list></app-basin-list>
    //   </div>
    // `,
    template: `
    <app-navbar></app-navbar>
    <!-- <h1>{{title}}</h1> -->
    <br><br>
    <router-outlet></router-outlet>
    <div>
      <button (click)="logout()">LOGOUT</button>
    </div>
  `,
    // styleUrl: './app.component.css'
    styles: ['h1 { color: blue; }'],
    imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive, NavbarComponent]
})
export class AppComponent  implements OnInit{
  title = 'Hydrological Alert Authoring System (HAAS)';
  isAuthenticated = false;

  constructor(private oauthService: OAuthService, private httpClient: HttpClient) { }

  logout() {
    this.oauthService.logOut();
  }

  // example of passing the access token to the backend
  getHelloText() {
    this.httpClient.get<{ message: string }>('http://localhost:3003', {
      headers: {
        'Authorization': `Bearer ${this.oauthService.getAccessToken()}`
      }
    }).subscribe(result => {
      this.title = result.message;
    });
  }

  ngOnInit(): void {}

  get_title() {
    return this.title;
  }

}
