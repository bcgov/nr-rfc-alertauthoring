import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';


@Component({
  selector: 'app-basin-item',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './basin-item.component.html',
  styleUrl: './basin-item.component.css'
})
export class BasinItemComponent {
  @Input() basin: any;
}
