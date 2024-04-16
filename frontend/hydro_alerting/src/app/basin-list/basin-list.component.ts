import { Component, OnInit } from '@angular/core';
import { CommonModule,  } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive } from '@angular/router';
import { BasinItemComponent } from '../basin-item/basin-item.component';
import { BasinAddFormComponent } from '../basin-add-form/basin-add-form.component';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { Observable } from 'rxjs';
import {map} from 'rxjs/operators';
import { BasinService } from '../services/basin.service';
import { Basin } from '../types/basin';

@Component({
  selector: 'app-basin-list',
  standalone: true,
  imports: [
    CommonModule, 
    BasinItemComponent, 
    BasinAddFormComponent, 
    FormsModule, 
    ReactiveFormsModule,
    RouterOutlet, RouterLink, RouterLinkActive],
  // the square brackets around [basin] tell angular that basin is an input 
  // property
  template: `
    <h2> Basins <Label><h2>
      <app-basin-add-form (addBasin)="onAddBasin($event)"></app-basin-add-form>
      <ul>
        <app-basin-item
          *ngFor="let basin of basins | async"
          [basin]="basin"
        ></app-basin-item>
      </ul>
  `,
  styles: []
})

export class BasinListComponent implements OnInit {
  // basinForm = new FormGroup({});
  // basinForm: FormGroup;
  // the ! tells the typscript that this property will have a property at runtime
  basins!: Observable<Basin[]>;

  constructor(private basinService: BasinService) {
    // this.basins = this.basinService.getBasins();
    // this.basins = [];
  }

  onAddBasin(basinData: any) {
    console.log("added new basin: " + JSON.stringify(basinData));
    // this.basinService.addBasin(basinData);
  }

  ngOnInit(): void {
    // this.basinService.getBasins().subscribe(basins => {
    //   this.basins = basins;
    // });

    // this.basins = this.basinService.getBasins();

    this.basins = this.basinService.getBasins().pipe(map((basins) => {
      return basins.map((basin) => {
        if (basin.id) { 
          basin.streak = basin.id <= 2 ? true : false;
          console.log('basin after streak added: ' + JSON.stringify(basin));
        }
        return basin;
      })
    }));

    //console.log("basins: " + JSON.stringify(this.basins));
  }

}
