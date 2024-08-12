import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { ActivatedRoute, Params, Router } from '@angular/router';
import { AlertService } from '../alert.service';
import { switchMap, Observable, of } from 'rxjs';
import { Alert } from '../../types/alert';
import { ReactiveFormsModule, FormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import Quill from 'quill'
import { MatQuillModule } from '../../mat-quill/mat-quill-module'
import { ContentChange, SelectionChange, QuillEditorComponent } from 'ngx-quill'
import {AuthzService} from '../../services/authz.service';

import { ViewMapComponent } from '../../view-map/view-map.component';

import dayjs from 'dayjs';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import utc from 'dayjs/plugin/utc';
import timezone from 'dayjs/plugin/timezone';


import {ViewBasinLevelComponent} from '../../basin-alerts/view-basin-level/view-basin-level.component';

@Component({
  selector: 'app-view-alert',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    FormsModule,
    CommonModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    QuillEditorComponent,
    MatQuillModule,
    ViewBasinLevelComponent,
    ViewMapComponent,
    ],
  templateUrl: './view-alert.component.html',
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  styleUrl: './view-alert.component.css',
})
export class ViewAlertComponent {
  alert_id: number | undefined;
  alert!: Observable<Alert>;
  form_disabled: string | null = 'disabled';
  single_alert_form: FormGroup;
  alert_description: string = "";
  alert_author : string = "";

  meteorological_data_contents: string = "";
  hydrological_data_contents: string = "";
  addinfo_data_contents?: string = "";

  // used to keep track if session has been authenticated
  authenticated: boolean = false;
  is_authorized = false;


  constructor(
      private route: ActivatedRoute, 
      private alertService: AlertService,
      private formBuilder: FormBuilder, 
      private authzService: AuthzService, 
      private router: Router) {
    this.single_alert_form = this.formBuilder.group({
      alert_data: of(alert)
    });
    console.log(`view alert data: ${JSON.stringify(this.alert)}`)
  }

  ngOnInit(): void {
    // retrieve the route params to find out what alert id has been selected
    // to be displayed, then passing that to the getAlert method of the 
    // alertService to retrieve the alert data to be displayed
    // this.editable = "readonly";
    this.route.params.pipe(
      switchMap((params: Params) => {
        // use params here
        console.log('params: ' + JSON.stringify(params));
        this.alert_id = params['id'];
        return this.alertService.getAlert(params['id']);
      }))
      .subscribe((alert: Alert) => {
        console.log('alert: ' + JSON.stringify(alert));
        this.meteorological_data_contents = alert.alert_meteorological_conditions;
        this.hydrological_data_contents = alert.alert_hydro_conditions;
        this.addinfo_data_contents = alert.additional_information;
        this.alert_description = alert.alert_description;
        this.alert_author = alert.author_name;
        this.alert = of(alert);
      });

      this.authzService.canEdit().subscribe((authData) => {
        console.log("GETTING DATA FROM SERVICE: " + JSON.stringify(authData));
        this.is_authorized = authData;
      });
  
  
  }

  /**
   * 
   * @param date input datestring in the format of "YYYY-MM-DDTHH:MM:SS.SSSSSS"
   * @returns date string in the format of "ddd MMM D, YYYY HH:MM:ss"
   */
  format_date(date: string) {
    // require('dayjs/locale/utc')
    //console.log("date: " + date);
    dayjs.extend(customParseFormat);
    dayjs.extend(utc);
    dayjs.extend(timezone);

    let date_format_string = "YYYY-MM-DDTHH:mm:ss.SSSSSS";
    // dateformat out of api: 2024-08-02T18:38:31.323767
    //                        2024-08-02T18:39:54.078208
    //"YYYY-MM-DDTHH:mm:ss.SSSSSS"
    // parse utc date
    let date_djs = dayjs.utc(date, date_format_string);

    // render as local date
    // let date_str = date_djs.local().format(date_format_string);
    // return date_str;

    // return as a date and have the browser render the date
    let return_date = date_djs.local().toDate();
    return return_date;
  }

  /**
   * 
   * triggers the edit session / route to ./edit route
   */
  route_to_edit() {
    let edit_path: string = "/alert/" + this.alert_id + "/edit"
    console.log(`navigate to: ${edit_path}`);
    this.router.navigate([edit_path])
  }

}
