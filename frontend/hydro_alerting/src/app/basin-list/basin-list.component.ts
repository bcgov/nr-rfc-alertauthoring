import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { BasinItemComponent } from '../basin-item/basin-item.component';
import { FormBuilder, FormGroup, FormsModule, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-basin-list',
  standalone: true,
  imports: [CommonModule, BasinItemComponent, FormsModule, ReactiveFormsModule],
  // the square brackets around [basin] tell angular that basin is an input 
  // property
  template: `
    <h2> Basins <Label><h2>
      <form [formGroup]="basinForm" (ngSubmit)="onSubmit(basinForm.value)">
        <input type="text" placeholder="Add Basin" formControlName="name"/>
        <button type="submit">Add</button>
      </form>
      <ul>
        <app-basin-item
          *ngFor="let basin of basins"
          [basin]="basin"
        ></app-basin-item>
      </ul>
  `,
  styles: []
})

export class BasinListComponent implements OnInit {
  // basinForm = new FormGroup({});
  basinForm: FormGroup;


  basins = [
    {
      id: 1,
      name: 'basin 1'
    },
    {
      id: 2,
      name: 'basin 2'
    },
    {
      id: 3,
      name: 'basin 33'
    },
    {
      id: 4,
      name: 'silly basin'
    }
  ];

  constructor(private formBuilder: FormBuilder) {
    this.basinForm = this.formBuilder.group({
      name: '',
    });
   }

   onSubmit(basinData: any) {
    console.log('Your basin has been submitted', basinData);
    const basin_id = this.basins.length + 1;
    basinData.id = basin_id;
    this.basins.push(basinData);
    this.basinForm.reset();
   }

  ngOnInit(): void {
    console.log("basins: " + JSON.stringify(this.basins));
  }

}
