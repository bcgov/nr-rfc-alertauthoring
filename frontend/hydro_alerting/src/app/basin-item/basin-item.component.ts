import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Basin } from '../basin';

@Component({
  selector: 'app-basin-item',
  standalone: true,
  imports: [CommonModule],
  template: `
    <li [style.color]="basin.streak ? 'red': 'black' ">
    <!-- <li> -->
      {{ basin.basin_name }}
    </li>
  `,
  styles: []
})

export class BasinItemComponent {
  @Input() basin!: Basin;
}
