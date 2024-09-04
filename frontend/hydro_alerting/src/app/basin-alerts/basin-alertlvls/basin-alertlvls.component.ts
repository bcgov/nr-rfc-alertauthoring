import { Component,  inject, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AsyncPipe, NgComponentOutlet } from '@angular/common';
import { MatButton } from '@angular/material/button';

import {BasinLvlDataService} from '../../services/basin-lvl-data.service';


// basin-alertlvls
@Component({
  selector: 'app-basin-alertlvls',
  standalone: true,
  imports: [NgComponentOutlet, MatButton, CommonModule, AsyncPipe],
  // providers: [BasinLvlDataService],
  templateUrl: './basin-alertlvls.component.html',
  styleUrl: './basin-alertlvls.component.css'
})
export class BasinAlertlvlsComponent implements AfterViewInit{

  compService = inject(BasinLvlDataService);
  comps = this.compService.getAllComponents();
  private currentIndex = 0;

  constructor(private basinLvlDataService: BasinLvlDataService) {
    console.log("basin data service constructor called");
  }

  ngAfterViewInit(): void {
    console.log("After view init called");
    // making sure there is always at least one alert selector loaded when
    // the page is loaded
    if (this.comps.length === 0) {
      this.addNewBasinAlertSelector();
    }
  }

  addNewBasinAlertSelector() {
    console.log("Add button pressed");
    this.basinLvlDataService.addNewBasinAlertSelector();
  }

}
