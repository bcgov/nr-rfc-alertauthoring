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
import { EditorChangeContent, EditorChangeSelection, QuillEditorComponent } from 'ngx-quill'
import { OidcSecurityService } from 'angular-auth-oidc-client';
import { ViewBasinLevelComponent } from '../view-basin-level/view-basin-level.component';


import dayjs from 'dayjs';
import customParseFormat from 'dayjs/plugin/customParseFormat';
import utc from 'dayjs/plugin/utc';




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
    ViewBasinLevelComponent],
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
  

  meteorological_data_contents: string = "";
  hydrological_data_contents: string = "";

  // used to keep track if session has been authenticated
  authenticated: boolean = false;


  constructor(
      private route: ActivatedRoute, 
      private alertService: AlertService,
      private formBuilder: FormBuilder, 
      private oidcSecurityService: OidcSecurityService, 
      private router: Router) {
    this.single_alert_form = this.formBuilder.group({
      alert_data: of(alert)
    });
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
        this.alert_description = alert.alert_description;
        this.alert = of(alert);
      });

      this.oidcSecurityService.isAuthenticated$.subscribe((isAuthenticated) => {
        console.log("is authenticated", isAuthenticated.isAuthenticated);
        this.authenticated = isAuthenticated.isAuthenticated;
      });
  
  }



  

  // isAuthenticated() {
  //   return this.authenticated;
  // }

  /**
   * 
   * @param date input datestring in the format of "YYYY-MM-DDTHH:MM:SS.SSSSSS"
   * @returns date string in the format of "ddd MMM D, YYYY HH:MM:ss"
   */
  format_date(date: string) {
    //console.log("date: " + date);
    dayjs.extend(customParseFormat);
    let date_djs = dayjs(date, "YYYY-MM-DDTHH:MM:SS.SSSSSS");
    // console.log("date_djs: " + date_djs);
    // TODO: all dates are in UTC atm... long term likely want to convert to 
    //       local time zone
    let date_str = date_djs.format('HH:MM:ss ddd MMM D, YYYY');
    return date_str;
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
