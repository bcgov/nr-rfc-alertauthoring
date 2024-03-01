import { Component, OnInit } from '@angular/core';
import { BasinService } from '../services/basin.service';
import { Observable } from 'rxjs';
import { Basin } from '../types/basin';
import { map } from 'rxjs/operators';
import {MatInputModule} from '@angular/material/input';
import {MatSelectModule} from '@angular/material/select';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatButtonModule} from '@angular/material/button';

import { ReactiveFormsModule } from '@angular/forms';
import { CommonModule,  } from '@angular/common';
import {FormsModule} from '@angular/forms';


@Component({
  selector: 'app-basin-alertlvl',
  standalone: true,
  imports: [
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule, 
    MatButtonModule,
    FormsModule,
    CommonModule],
  templateUrl: './basin-alertlvl.component.html',
  styleUrl: './basin-alertlvl.component.css'
})
export class BasinAlertlvlComponent {
  basins!: Observable<Basin[]>;


  constructor(private basinService: BasinService) {
  }


  ngOnInit(): void {
    this.basins = this.basinService.getBasins().pipe(map((basins) => {
      return basins.map((basin: Basin) => {
        basin.streak = basin.id <= 2 ? true : false;
        console.log('basin after streak added: ' + JSON.stringify(basin));
        return basin;
      })
    }));
  }

  addNewBasinAlertSelector() {
    console.log('addNewBasinAlertSelector');
  }



}
