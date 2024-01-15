import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';

import { BasinListComponent } from './basin-list/basin-list.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, BasinListComponent, ReactiveFormsModule],
  // templateUrl: './app.component.html',
  template: `
    <div class="container">
    <h1>{{title}}</h1>
    <app-basin-list></app-basin-list>
    </div>
  `,
  // styleUrl: './app.component.css'
  styles: ['h1 { color: blue; }']
})
export class AppComponent {
  title = 'Hydrological Alert Authoring System (HAAS)';
}
