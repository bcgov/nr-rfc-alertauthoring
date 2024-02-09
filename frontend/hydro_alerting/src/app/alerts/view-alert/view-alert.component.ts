import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Params } from '@angular/router';
import { AlertService } from '../alert.service';
import { switchMap, Observable, of } from 'rxjs';
import { Alert } from '../../alert';
import { ReactiveFormsModule, FormsModule, FormBuilder, FormGroup } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { CommonModule } from '@angular/common';
import {MatButtonModule} from '@angular/material/button';


@Component({
  selector: 'app-view-alert',
  standalone: true,
  imports: [ReactiveFormsModule, FormsModule, CommonModule, MatFormFieldModule, MatInputModule, MatButtonModule ],
  templateUrl: './view-alert.component.html',
  styleUrl: './view-alert.component.css',
})
export class ViewAlertComponent {
typeof(arg0: string|null) {
throw new Error('Method not implemented.');
}
  alert_id: number | undefined;
  alert!: Observable<Alert>;
  editable: string | null = null;//"readonly";
  form_disabled: string | null = 'disabled';
  single_alert_form: FormGroup;

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
      .subscribe((alert) => {
        console.log('alert: ' + JSON.stringify(alert));
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
    } else {
      this.form_disabled = 'disabled';
    }
  }

  format_date(date: string) {
    // converts the date string to a date object, then spits back out 
    // according to the format requested
    console.log("date: " + date);
    return "";
  } 

}
