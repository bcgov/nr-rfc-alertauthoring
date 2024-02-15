import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Params, Router } from '@angular/router';
import { switchMap, Observable, of } from 'rxjs';
import { Alert } from '../../alert';
import { AlertService } from '../alert.service';
import { FormGroup, FormBuilder ,FormsModule, Validators} from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatButton } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { ReactiveFormsModule } from '@angular/forms';
import dayjs from 'dayjs';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import {MatSelectModule} from '@angular/material/select';

import Quill from 'quill'
import { MatQuillModule } from '../../mat-quill/mat-quill-module'
import { MatQuill } from '../../mat-quill/mat-quill'

import { EditorChangeContent, EditorChangeSelection, QuillEditorComponent } from 'ngx-quill'

// 
@Component({
  selector: 'app-edit-alert',
  standalone: true,
  imports: [
    CommonModule, 
    MatInputModule, 
    MatFormFieldModule, 
    ReactiveFormsModule, 
    MatSelectModule,
    QuillEditorComponent,
    
    MatQuillModule,
    FormsModule,
    MatButton,
  ],
  templateUrl: './edit-alert.component.html',
  styleUrl: './edit-alert.component.css',
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
})
export class EditAlertComponent implements OnInit {
  alert!: Observable<Alert>;
  alert_id: number | undefined;
  edit_alert_form: FormGroup;
  alert_create_date!: Date;
  alert_updated_date!: Date;
  meteorological_data_contents!: string;
  hydrological_data_contents!: string;


  @ViewChild('meteorologicalDataEditor', {
    static: true
  }) meteorologicalDataEditor: MatQuill | undefined




  test_param: string = "test";

  constructor(
    private route: ActivatedRoute,
    private alertService: AlertService,
    private formBuilder: FormBuilder,

  ) {
    this.edit_alert_form = this.formBuilder.group({
      // meteorological_data_contents: this.alert?.alert_meteorological_conditions,
      alert_data: of(alert),
      alert_description: ["",],
      meteorological_data_contents: ["",],
      hydrological_data_contents: ["",],
      alert_status: ["",],
      meteorologicalDataEditor: [""],
    });
  }

  ngOnInit(): void {
    this.route.params.pipe(
      switchMap((params: Params) => {
        console.log('params: ' + JSON.stringify(params));
        this.alert_id = params['id'];
        return this.alertService.getAlert(params['id']);
      }))
      .subscribe((alert: Alert) => {
        console.log('alert: ' + JSON.stringify(alert));
        dayjs.extend(customParseFormat);
        this.test_param = "test";
        this.alert_create_date = dayjs(alert.alert_created, "YYYY-MM-DDTHH:MM:SS.SSSSSS").toDate();
        this.alert_updated_date = dayjs(alert.alert_updated, "YYYY-MM-DDTHH:MM:SS.SSSSSS").toDate();
        this.hydrological_data_contents = alert.alert_hydro_conditions;
        this.meteorological_data_contents = alert.alert_meteorological_conditions;
        // example of setting a property on the form object
        this.edit_alert_form.controls['alert_description'].setValue(alert.alert_description);
        this.edit_alert_form.controls['meteorologicalDataEditor'].setValue(alert.alert_meteorological_conditions);

        this.alert = of(alert);
      });

  }

  onSubmit() {
    // example for capture a property from the form object
    console.log(`form data: ${this.edit_alert_form.value.alert_description}`);
    console.log(`form data: ${JSON.stringify(this.edit_alert_form.value)}`);

    this.alert.subscribe((alert: Alert) => {
      // console.log('alert: ' + JSON.stringify(alert));
      console.log(`alert description: ${alert.alert_description}`);
    });
  }

  onChange(e: any) {
    console.log(`onChange: ${JSON.stringify(e)}`);
    console.log(`form data: ${JSON.stringify(this.edit_alert_form)}`);
  }

  resetForm() {
    // reset the values in the form back to original values
    this.alert.subscribe((alert: Alert) => {
      // console.log('alert: ' + JSON.stringify(alert));
      console.log(`alert description: ${alert.alert_description}`);
      this.edit_alert_form.patchValue({
        hydrological_data_contents: alert.alert_hydro_conditions,
        meteorological_data_contents: alert.alert_meteorological_conditions,
        alert_description: alert.alert_description,
        alert_status: alert.alert_status,
      });
    });
  }

}
