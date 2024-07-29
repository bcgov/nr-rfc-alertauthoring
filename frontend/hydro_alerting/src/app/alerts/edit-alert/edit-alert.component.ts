import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Params, Router } from '@angular/router';
import { switchMap, Observable, of } from 'rxjs';
import { Alert, AlertAreaLevels, AlertCreate } from '../../types/alert';
import { FormGroup, FormControl, FormBuilder, FormsModule, Validators } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatButton } from '@angular/material/button';
import { MatFormFieldModule } from '@angular/material/form-field';
import { ReactiveFormsModule } from '@angular/forms';
import dayjs from 'dayjs';
import timezone from 'dayjs/plugin/timezone'
dayjs.extend(timezone); // use plugin

import customParseFormat from 'dayjs/plugin/customParseFormat';
import { MatSelectModule } from '@angular/material/select';
import { BasinLvlDataService } from '../../services/basin-lvl-data.service';

import Quill from 'quill'
import { MatQuillModule } from '../../mat-quill/mat-quill-module'
import { MatQuill } from '../../mat-quill/mat-quill'

import { BasinAlertlvlsComponent } from '../../basin-alerts/basin-alertlvls/basin-alertlvls.component';
import { EditorChangeContent, EditorChangeSelection, QuillEditorComponent } from 'ngx-quill'
import { TokenHelperService } from 'angular-auth-oidc-client/lib/utils/tokenHelper/token-helper.service';
import { AuthzService } from '../../services/authz.service';
import { AlertsService } from '../../services/alerts.service';
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
    BasinAlertlvlsComponent,
  ],
  templateUrl: './edit-alert.component.html',
  styleUrl: './edit-alert.component.css',
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
})
export class EditAlertComponent implements OnInit {
  alert!: Observable<Alert>;
  alert_id!: number;
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
  @ViewChild('addInfoDataEditor', {
    static: true
  }) addInfoDataEditor: MatQuill | undefined


  test_param: string = "test";

  constructor(
    private route: ActivatedRoute,
    private alertService: AlertsService,
    private router: Router, 
    private formBuilder: FormBuilder,
    private basinLvlDataService: BasinLvlDataService,
    private authzService: AuthzService,
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
      addInfoDataEditor: [""],
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
        this.edit_alert_form.setControl('addInfoDataEditor', new FormControl(alert.additional_information))

        this.basinLvlDataService.setBasinAlertlvlComponentData(alert.alert_links);
        this.alert = of(alert);
      });

  }

  onSubmit() {
    // example for capture a property from the form object
    // console.log(`form data: ${this.edit_alert_form.value.alert_description}`);
    // console.log(`form data: ${JSON.stringify(this.edit_alert_form.value)}`);

    // this.alert.subscribe((alert: Alert) => {
      // console.log('alert: ' + JSON.stringify(alert));
    //console.log(`alert description: ${alert.alert_description}`);
    let basinAlertLevelData: AlertAreaLevels[] = this.basinLvlDataService.getAllBasinAlertLvlData();

    let edit_alert: AlertCreate = {
      alert_description: this.edit_alert_form.value.alert_description,
      alert_status: this.edit_alert_form.value.alert_status,
      alert_hydro_conditions: this.edit_alert_form.value.meteorologicalDataEditor,
      alert_meteorological_conditions: this.edit_alert_form.value.hydrologicalDataEditor,
      additional_information: this.edit_alert_form.value.addInfoDataEditor,
      alert_links: this.basinLvlDataService.getAllBasinAlertLvlData(),
      author_name: this.authzService.payload.display_name,
    }
    // alert id from this.alert_id
    this.alertService.editAlert(edit_alert, this.alert_id).subscribe((data) => {
      console.log(`data from post: ${JSON.stringify(data)}`);
      // this.alert_data = data.alert_id;
      this.router.navigate(['/alert', data.alert_id]);
    });
  
      // this is where the api call will take place to update the alert

  }

  onChange(e: any) {
    // console.log(`onChange: ${JSON.stringify(e)}`);
    // console.log(`form data: ${JSON.stringify(this.edit_alert_form)}`);
  }

  resetForm() {
    // reset the values in the form back to original values, original values come
    // from the alert observable
    this.alert.subscribe((alert: Alert) => {
      console.log(`alert description: ${alert.alert_description}`);
      this.edit_alert_form.get('meteorologicalDataEditor')!.patchValue(alert.alert_meteorological_conditions);
      this.edit_alert_form.get('hydrologicalDataEditor')!.patchValue(alert.alert_hydro_conditions);
      this.edit_alert_form.get('addInfoDataEditor')!.patchValue(alert.additional_information);
      this.edit_alert_form.get('alert_status')!.patchValue(alert.alert_status);
      this.edit_alert_form.get('alert_description')!.patchValue(alert.alert_description);
    });
  }

  submit_edits() {
    // TODO: need to pass the values onto the api
    // console.log(`form data: ${JSON.stringify(this.edit_alert_form.value)}`);
    // console.log(`alert description: ${this.edit_alert_form.value.alert_description}`);
    // pass the json contained in: this.edit_alert_form.value to the api
  }
}
