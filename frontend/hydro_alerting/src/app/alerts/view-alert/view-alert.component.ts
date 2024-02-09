import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA } from '@angular/core';
import { ActivatedRoute, Params } from '@angular/router';
import { AlertService } from '../alert.service';
import { switchMap, Observable, of } from 'rxjs';
import { Alert } from '../../alert';
import { ReactiveFormsModule, FormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import Quill from 'quill'
import { MatQuillModule } from '../../mat-quill/mat-quill-module'
import { EditorChangeContent, EditorChangeSelection, QuillEditorComponent } from 'ngx-quill'
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
    MatFormFieldModule],
  templateUrl: './view-alert.component.html',
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  styleUrl: './view-alert.component.css',
})
export class ViewAlertComponent {
  typeof(arg0: string | null) {
    throw new Error('Method not implemented.');
  }
  alert_id: number | undefined;
  alert!: Observable<Alert>;
  editable: string | null = null;//"readonly";
  form_disabled: string | null = 'disabled';
  single_alert_form: FormGroup;

  meteorological_data_contents: string = "";
  hydrological_data_contents: string = "";

  // quill component properties
  blurred = false;
  focused = false;
  quillReadonly=true;


  constructor(private route: ActivatedRoute, private alertService: AlertService, private formBuilder: FormBuilder) {
    this.single_alert_form = this.formBuilder.group({
      some_value: this.editable,
      disabled: true,
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
        this.alert = of(alert);
      });
    this.single_alert_form.disable();
  }

  onEnableEditing() {
    if (this.editable === "readonly") {
      this.editable = null;
    } else {
      this.editable = "readonly";
    }
    if (this.form_disabled === 'disabled') {
      this.form_disabled = null;
      this.quillReadonly = false;
    } else {
      this.form_disabled = 'disabled';
      this.quillReadonly = true;
    }
  }

  /**
   * 
   * @param date input datestring in the format of "YYYY-MM-DDTHH:MM:SS.SSSSSS"
   * @returns date string in the format of "ddd MMM D, YYYY HH:MM:ss"
   */
  format_date(date: string) {
    console.log("date: " + date);
    dayjs.extend(customParseFormat);
    let date_djs = dayjs(date, "YYYY-MM-DDTHH:MM:SS.SSSSSS");
    console.log("date_djs: " + date_djs);
    // TODO: all dates are in UTC atm... long term likely want to convert to 
    //       local time zone
    let date_str = date_djs.format('HH:MM:ss ddd MMM D, YYYY');
    return date_str;
  }


// -------------------------- Quill components --------------------------


  changedEditor(event: EditorChangeContent | EditorChangeSelection | any) {
    // tslint:disable-next-line:no-console
    console.log('editor-change', event)
  }

  focus($event: any) {
    // tslint:disable-next-line:no-console
    console.log('focus', $event)
    this.focused = true
    this.blurred = false
  }
  nativeFocus($event: any) {
    // tslint:disable-next-line:no-console
    console.log('native-focus', $event)
  }

  blur($event: any) {
    // tslint:disable-next-line:no-console
    console.log('blur', $event)
    this.focused = false
    this.blurred = true
  }
  nativeBlur($event: any) {
    // tslint:disable-next-line:no-console
    console.log('native-blur', $event)
  }

  created(editor: any) {
    const range = editor.getSelection(true)
    
    // editor.insertText(0, this.meteorological_data_contents)
  }

}
