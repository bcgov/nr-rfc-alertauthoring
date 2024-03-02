import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AsyncPipe, NgComponentOutlet } from '@angular/common';
import { MatButton } from '@angular/material/button';

import {BasinLvlService } from '../services/basin-lvl.service';
import { BasinAlertlvlComponent } from '../basin-alertlvl/basin-alertlvl.component';

@Component({
  selector: 'app-basin-lvl',
  standalone: true,
  imports: [NgComponentOutlet, AsyncPipe, MatButton, CommonModule],
  templateUrl: './basin-lvl.component.html',
  styleUrl: './basin-lvl.component.css'
})
export class BasinLvlComponent {
  private basinlvlList = inject(BasinLvlService).getBasinLevels();
  private currentIndex = 0;

  get all() {
    return this.basinlvlList;
  }
  get currentAd() {
    return this.basinlvlList[this.currentIndex];
  }

  addNewBasinAlertSelector() {
    console.log("button pressed");
    this.basinlvlList.push(
      {
        component: BasinAlertlvlComponent,
        inputs: { basin_name: '', alert_level: '' }
      } as {component: any, inputs: Record<string, any>}
      )
  }

  ondelete() {
    console.log("delete button pressed in child component");
    // this.basinlvlList.splice(this.currentIndex, 1);
  }

}
