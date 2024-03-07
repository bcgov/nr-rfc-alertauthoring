import { Component,  inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AsyncPipe, NgComponentOutlet } from '@angular/common';
import { MatButton } from '@angular/material/button';

// import { BasinAlertlvlComponent } from '../basin-alertlvl/basin-alertlvl.component';
import {BasinLvlDataService} from '../services/basin-lvl-data.service';
import { Observable, of } from 'rxjs';

@Component({
  selector: 'app-basin-lvl',
  standalone: true,
  imports: [NgComponentOutlet, MatButton, CommonModule, AsyncPipe],
  providers: [BasinLvlDataService],
  templateUrl: './basin-lvl.component.html',
  styleUrl: './basin-lvl.component.css'
})
export class BasinLvlComponent {

  compService = inject(BasinLvlDataService);
  comps = this.compService.getAllComponents();
  private currentIndex = 0;

  constructor(private basinLvlDataService: BasinLvlDataService) {
    console.log("basin data service constructor called");
  }

  addNewBasinAlertSelector() {
    console.log("Add button pressed");
    this.basinLvlDataService.addNewBasinAlertSelector();
  }

}
