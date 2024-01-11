import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';

import { BasinListComponent } from './basin-list/basin-list.component';
import { BasinItemComponent } from './basin-item/basin-item.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, BasinListComponent, BasinItemComponent, ReactiveFormsModule],
  // templateUrl: './app.component.html',
  template: `<h1>{{title}}</h1>
    <app-basin-list></app-basin-list> 
  `,
  // styleUrl: './app.component.css'
  styles: ['h1 { color: blue; }']
})
export class AppComponent {
  title = 'Hydrological Alert Authoring System (HAAS)';
}
