import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, Params } from '@angular/router';
import { AlertService } from '../alert.service';
import { switchMap, Observable, of } from 'rxjs';
import { Alert } from '../../alert';
import { ReactiveFormsModule, FormsModule, FormBuilder } from '@angular/forms';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
// import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { CommonModule } from '@angular/common';
// import { trigger, transition, style, animate } from '@angular/animations';


@Component({
  selector: 'app-view-alert',
  standalone: true,
  imports: [ReactiveFormsModule, FormsModule, CommonModule ],
  templateUrl: './view-alert.component.html',
  styleUrl: './view-alert.component.css',
  // animations: [
  //   trigger('transitionMessages', [
  //     transition(':enter', [
  //       style({ opacity: 0 }),
  //       animate('500ms', style({ opacity: 1 })),
  //     ]),
  //     transition(':leave', [
  //       animate('500ms', style({ opacity: 0 }))
  //     ])
  //   ])
  // ]
})
export class ViewAlertComponent {
  alert_id: number | undefined;
  alert!: Observable<Alert>;
  // alert!: Alert;
  form: any;
  editable: string | null = "readonly";
  single_alert_form: any;


  constructor(private route: ActivatedRoute, private alertService: AlertService, private formBuilder: FormBuilder) {
    this.single_alert_form = this.formBuilder.group({
      editable: "readonly",
    });

  }

  ngOnInit(): void {
    // retrieve the route params to find out what alert id has been selected
    // to be displayed, then passing that to the getAlert method of the 
    // alertService to retrieve the alert data to be displayed
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

  }
}
