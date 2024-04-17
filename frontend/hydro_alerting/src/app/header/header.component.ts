import { Component } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButton } from '@angular/material/button';
import { RouterLink, RouterOutlet } from '@angular/router';


@Component({
  selector: 'app-header',
  standalone: true,
  imports: [MatToolbarModule, MatButton, RouterLink, RouterOutlet],
  templateUrl: './header.component.html',
  styleUrl: './header.component.css'
})
export class HeaderComponent {
  title = "Hydrological Alert Authoring System"
}
