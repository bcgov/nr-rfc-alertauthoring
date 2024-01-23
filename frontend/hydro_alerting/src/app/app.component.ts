import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
// import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
// import { ReactiveFormsModule } from '@angular/forms';
import { RouterOutlet } from '@angular/router';

// import { Observable } from 'rxjs';
import { OAuthService } from 'angular-oauth2-oidc';
import { HttpClient, HttpHeaders } from '@angular/common/http';




// import { BasinListComponent } from './basin-list/basin-list.component';

@Component({
  selector: 'app-root',
  standalone: true,
  // imports: [CommonModule, RouterOutlet, BasinListComponent, ReactiveFormsModule],
  // templateUrl: './app.component.html',
  imports: [CommonModule, RouterOutlet],

  // template: `
  //   <div class="container">
  //   <h1>{{title}}</h1>
  //   <app-basin-list></app-basin-list>
  //   </div>
  // `,
  template: `
    <h1>{{title}}</h1>
    <br><br>
    <router-outlet></router-outlet>
    <div>
      <button (click)="logout()">LOGOUT</button>
    </div>
  `,

  // styleUrl: './app.component.css'
  styles: ['h1 { color: blue; }']
})
export class AppComponent  {
  title = 'Hydrological Alert Authoring System (HAAS)';
  isAuthenticated = false;

  constructor(private oauthService: OAuthService, private httpClient: HttpClient) { }

  logout() {
    this.oauthService.logOut();
  }

  getHelloText() {
    this.httpClient.get<{ message: string }>('http://localhost:3003', {
      headers: {
        'Authorization': `Bearer ${this.oauthService.getAccessToken()}`
      }
    }).subscribe(result => {
      this.title = result.message;
    });
  }

}
