import { Component, OnInit, CUSTOM_ELEMENTS_SCHEMA, inject  } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormGroup, FormBuilder, FormsModule, FormControl, ReactiveFormsModule } from '@angular/forms';
import { Router } from '@angular/router';

// angular material specific imports
import { MatInputModule } from '@angular/material/input';
import { MatButton } from '@angular/material/button';
import {MatSelectModule} from '@angular/material/select';

// quill specific imports for the editor
import Quill from 'quill'
import { MatQuillModule } from '../../mat-quill/mat-quill-module'
import { MatQuill } from '../../mat-quill/mat-quill'
import { EditorChangeContent, EditorChangeSelection, QuillEditorComponent } from 'ngx-quill'

// basin alertlvl specific imports
// import { BasinAlertlvlMultiComponent } from '../../basin-alertlvl-multi/basin-alertlvl-multi.component';
import {BasinAlertlvlsComponent} from '../../basin-alerts/basin-alertlvls/basin-alertlvls.component';

@Component({
  selector: 'app-create-alert',
  standalone: true,
  imports: [
    FormsModule, 
    CommonModule, 
    ReactiveFormsModule, 
    MatInputModule, 
    MatButton, 
    MatSelectModule,
    QuillEditorComponent,
    MatQuillModule,
    BasinAlertlvlsComponent,
    ],
  templateUrl: './create-alert.component.html',
  styleUrl: './create-alert.component.css',
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
})
export class CreateAlertComponent implements OnInit {

  create_alert_form: FormGroup;

  constructor(
      private formBuilder: FormBuilder,
      private router: Router) {
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
    // Todo: push this data to the api, the api should return the new alert id
    // that has been generated, then the route will navigate to the view alert
    console.log('Create Alert Form Submitted');
    console.log(`form data: ${JSON.stringify(this.create_alert_form.value)}`);
    // hard coding the redirect atm
    this.router.navigate(['/alert', '1']);
  }

  resetForm() {
    console.log("reset form")
    this.create_alert_form.get('alert_description')!.reset();
    this.create_alert_form.get('meteorologicalDataEditor')!.reset();
    this.create_alert_form.get('hydrologicalDataEditor')!.reset();
    this.create_alert_form.get('alert_status')!.reset();
  }

}
