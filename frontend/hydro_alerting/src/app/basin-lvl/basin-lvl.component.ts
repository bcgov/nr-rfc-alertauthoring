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
  //private basinlvlList = <any>[]
  // private basinlvlList!: Observable<any>;
  // private basinLvlService = inject(BasinLvlDataService);
  // private basinLvlCompService = inject(BasinLvlComponentService);

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




  // basinDataSvc.deleteSubject.subscribe(x => {
  //   console.log('From subscription 1:', x);
  //   for(let i=0; i<this.basinlvlList.length; i++){
  //     console.log("From subscription 2: ", i);
  //     console.log(`x is ${x}`);
  //     console.log(`curr indx is ${this.basinlvlList[i].inputs['basin_name']}`);
  //     console.log(`all date is: ${JSON.stringify(this.basinlvlList)}`)
  //     if (this.basinlvlList[i].inputs['basin_name'] === x) {
  //       if (i === 0) {
  //         console.log("reset the one entry in form");
  //         this.basinlvlList[i].inputs['basin_name'] = '';
  //         this.basinlvlList[i].inputs['alert_level'] = '';
  //       }
  //       this.basinlvlList.splice(i, 1);
  //       break;
  //     }
  //   }
  // });


}
