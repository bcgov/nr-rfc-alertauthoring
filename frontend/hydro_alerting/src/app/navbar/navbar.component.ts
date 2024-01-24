import { Component } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { RouterModule, RouterLink, RouterOutlet } from '@angular/router';
import { AppComponent } from '../app.component';

@Component({
  selector: 'app-navbar',
  standalone: true,
  imports: [MatToolbarModule, MatButtonModule, RouterLink, RouterOutlet],
  templateUrl: './navbar.component.html',
  styleUrl: './navbar.component.css'
})
export class NavbarComponent  {
  // todo: circle back here and make this a link to the original title for the app from the app.component.ts
  title = "Hydrological Alert Authoring System (HAAS)"

}
