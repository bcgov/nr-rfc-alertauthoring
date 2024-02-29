import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatButton } from '@angular/material/button';

import { FormGroup, FormBuilder, FormsModule, FormControl } from '@angular/forms';


@Component({
  selector: 'app-create-alert',
  standalone: true,
  imports: [FormsModule, CommonModule, ReactiveFormsModule, MatInputModule, MatButton],
  templateUrl: './create-alert.component.html',
  styleUrl: './create-alert.component.css',
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
})
export class CreateAlertComponent implements OnInit {

  create_alert_form: FormGroup;

  constructor(private formBuilder: FormBuilder) {
    this.create_alert_form = this.formBuilder.group({
      alert_description: ["",],
      alert_status: ["",],
      meteorologicalDataEditor: [""],
      hydrologicalDataEditor: [""],
    });
  }

  ngOnInit(): void {


  }

  onSubmitCreate() {
    console.log('Create Alert Form Submitted');
  }

  resetForm() {

  }

}
