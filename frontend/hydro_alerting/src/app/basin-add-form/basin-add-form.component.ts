import { Component, Output, EventEmitter } from '@angular/core';
import { FormBuilder, FormsModule, ReactiveFormsModule } from '@angular/forms';

@Component({
  selector: 'app-basin-add-form',
  standalone: true,
  imports: [FormsModule, ReactiveFormsModule],
  // templateUrl: './basin-add-form.component.html',
  template: `
    <form [formGroup]="basinForm" (ngSubmit)="onSubmit(basinForm.value)">
      <input type="text" placeholder="Add Basin" formControlName="name"/>
      <button type="submit">Add</button>
    </form>
  `,
  styles: [
    `
      button {
        background-color: blue;
        color: white;
        border-radius: 5px;
        font-size: 16px;
      }`
  ]
})
export class BasinAddFormComponent {
  basinForm:  any;
  @Output() addBasin = new EventEmitter<any>();
  
  constructor(private formBuilder: FormBuilder) {
    this.basinForm = this.formBuilder.group({
      name: '',
    });
  }

  onSubmit(newBasin: any) {
    console.log("new basin to submit: " + JSON.stringify(newBasin));
    this.addBasin.emit(newBasin);
    this.basinForm.reset();
  }

}
