import { Component, OnInit } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { RouterLink, RouterOutlet } from '@angular/router';
import { OidcSecurityService } from 'angular-auth-oidc-client';
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
  authenticated = false;
  login_logout_text = 'login';

  constructor(private oidcSecurityService: OidcSecurityService) { }


  ngOnInit(): void {
    this.oidcSecurityService
      .checkAuth()
      .subscribe(({ isAuthenticated, userData, accessToken }) => {
        this.authenticated = isAuthenticated;
        console.log('app authenticated', isAuthenticated, typeof (isAuthenticated));
        console.log(`Current access token is '${accessToken}'`);
        console.log(`User data: ${userData}`)
        if (isAuthenticated) {
          this.login_logout_text = "logout";
        }
      });
    // this.login_logout();
  }


  login_logout() {
    console.log("login_logout() called");
    if (this.authenticated) {
      this.oidcSecurityService.logoff().subscribe((result) => {
        console.log(result);
        this.login_logout_text = "login";
      });
    } else {
      this.oidcSecurityService.authorize();
      this.login_logout_text = "logout";
    }
  }
}
