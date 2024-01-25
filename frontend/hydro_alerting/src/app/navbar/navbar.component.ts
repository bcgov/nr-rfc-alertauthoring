import { Component, OnInit } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import {  RouterLink, RouterOutlet } from '@angular/router';
import { OAuthService, OAuthErrorEvent } from 'angular-oauth2-oidc';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [MatToolbarModule, MatButtonModule, RouterLink, RouterOutlet],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent implements OnInit {
  // todo: circle back here and make this a link to the original title for the app from the app.component.ts
  title = "Hydrological Alert Authoring System (HAAS)"
  loggedIn = false;
  login_logout_text = 'login';

  constructor(private oauthService: OAuthService, private httpClient: HttpClient) { }


  ngOnInit(): void {
    // this.oauthService.events.subscribe(event => {
    //   if (event instanceof OAuthErrorEvent) {
    //     console.error(`event error recieved  ${event}`);
    //   } else {
    //     console.warn(`event recieved  ${JSON.stringify(event)}`);
    //   }
    // });
    // if (this.oauthService.hasValidAccessToken()) {
    //   this.loggedIn = true;
    //   this.login_logout_text = "logout";
    // }
    this.login_logout()
        
  }


  login_logout() {
    console.log("login_logout() called");
    if (this.oauthService.hasValidAccessToken()) {
      this.oauthService.logOut();
      this.login_logout_text="logout";
      this.loggedIn = false;
      console.log("has valid token");
    } else {
      // this.oauthService.loadDiscoveryDocumentAndLogin();
      this.login_logout_text="login";
      this.loggedIn = true;

    }
  }

}
