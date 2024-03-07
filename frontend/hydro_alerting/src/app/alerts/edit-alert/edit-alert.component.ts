import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Params, Router } from '@angular/router';
import { switchMap, Observable, of } from 'rxjs';
import { Alert } from '../../types/alert';
import { AlertService } from '../alert.service';
import { FormGroup, FormControl, FormBuilder ,FormsModule, Validators} from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatButton } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { ReactiveFormsModule } from '@angular/forms';
import dayjs from 'dayjs';
import timezone from 'dayjs/plugin/timezone' 
dayjs.extend(timezone); // use plugin

import customParseFormat from 'dayjs/plugin/customParseFormat';
import {MatSelectModule} from '@angular/material/select';

import Quill from 'quill'
import { MatQuillModule } from '../../mat-quill/mat-quill-module'
import { MatQuill } from '../../mat-quill/mat-quill'

import { EditorChangeContent, EditorChangeSelection, QuillEditorComponent } from 'ngx-quill'
import { TokenHelperService } from 'angular-auth-oidc-client/lib/utils/tokenHelper/token-helper.service';
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
  local_tz: string;

  @ViewChild('meteorologicalDataEditor', {
    static: true
  }) meteorologicalDataEditor: MatQuill | undefined
  @ViewChild('hydrologicalDataEditor', {
    static: true
  }) hydrologicalDataEditor: MatQuill | undefined

  test_param: string = "test";

  constructor(
    private route: ActivatedRoute,
    private alertService: AlertService,
    private formBuilder: FormBuilder,
    

  ) {

    this.local_tz = dayjs.tz.guess();

    dayjs.tz.setDefault(this.local_tz);
    this.edit_alert_form = this.formBuilder.group({
      // meteorological_data_contents: this.alert?.alert_meteorological_conditions,
      alert_data: of(alert),
      alert_description: ["",],
      alert_status: ["",],
      meteorologicalDataEditor: [""],
      hydrologicalDataEditor: [""],
      alert_updated_date: [],
      alert_created_date: [],
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
        // convert the date to a Date object to send to the ui
        this.alert_create_date = dayjs(alert.alert_created, "YYYY-MM-DDTHH:MM:SS.SSSSSS").toDate();
        this.edit_alert_form.controls['alert_created_date'].setValue(dayjs().toDate());

        // example of setting a property on the form object
        this.edit_alert_form.controls['alert_description'].setValue(alert.alert_description);
        this.edit_alert_form.controls['alert_updated_date'].setValue(dayjs().toDate());
        this.edit_alert_form.controls['alert_status'].setValue(alert.alert_status);
        this.edit_alert_form.setControl('meteorologicalDataEditor', new FormControl(alert.alert_meteorological_conditions))
        this.edit_alert_form.setControl('hydrologicalDataEditor', new FormControl(alert.alert_hydro_conditions))    

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
    // reset the values in the form back to original values, original values come
    // from the alert observable
    this.alert.subscribe((alert: Alert) => {
      console.log(`alert description: ${alert.alert_description}`);
      this.edit_alert_form.get('meteorologicalDataEditor')!.patchValue(alert.alert_meteorological_conditions);
      this.edit_alert_form.get('hydrologicalDataEditor')!.patchValue(alert.alert_hydro_conditions);
      this.edit_alert_form.get('hydrologicalDataEditor')!.patchValue(alert.alert_hydro_conditions);
      this.edit_alert_form.get('alert_status')!.patchValue(alert.alert_status);
      this.edit_alert_form.get('alert_description')!.patchValue(alert.alert_description);
    });
  }

  submit_edits() {
    // TODO: need to pass the values onto the api
    console.log(`form data: ${JSON.stringify(this.edit_alert_form.value)}`);
    console.log(`alert description: ${this.edit_alert_form.value.alert_description}`);
    // pass the json contained in: this.edit_alert_form.value to the api
  }
}
