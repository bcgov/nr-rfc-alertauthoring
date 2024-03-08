import { Component } from '@angular/core';
import { AuthzService } from '../services/authz.service';

import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-unauthorized',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './unauthorized.component.html',
  styleUrl: './unauthorized.component.css'
})
export class UnauthorizedComponent {
  authN: boolean = false;
  authZ: boolean = false;
  given_name: string = "";
  payload: any = {}


  constructor(private authzService: AuthzService) {
    this.authZ = authzService.authorized;
    this.authN = authzService.authenticated;
    this.payload = JSON.stringify(authzService.payload);
    if (authzService.payload) {
      this.given_name = authzService.payload.given_name;
    }
  }


}
