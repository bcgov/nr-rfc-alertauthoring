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
import {BasinAlertlvlsComponent} from '../../basin-alerts/basin-alertlvls/basin-alertlvls.component';
import { AlertsService } from '../../services/alerts.service';
import {BasinLvlDataService} from '../../services/basin-lvl-data.service';
import { AlertAreaLevels, AlertCreate } from '../../types/alert';
import { AuthzService } from '../../services/authz.service';
import { CreateMapComponent } from '../../map/create-map/create-map.component';

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
    CreateMapComponent,
    ],
  templateUrl: './create-alert.component.html',
  styleUrl: './create-alert.component.css',
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
})
export class CreateAlertComponent implements OnInit {

  create_alert_form: FormGroup;
  alert_id: number | undefined;

  constructor(
      private formBuilder: FormBuilder,
      private router: Router, 
      private alertService: AlertsService,
      private authzService: AuthzService,
      private basinAlertLevelService: BasinLvlDataService) {
    this.create_alert_form = this.formBuilder.group({
      alert_description: ["",],
      alert_status: ["",],
      meteorologicalDataEditor: [""],
      hydrologicalDataEditor: [""],
      additionalInformationDataEditor: [""],
    });
    basinAlertLevelService.reset();
  }

  ngOnInit(): void {
    
  }

  onSubmitCreate() {
    // Todo: push this data to the api, the api should return the new alert id
    // that has been generated, then the route will navigate to the view alert
    console.log('Create Alert Form Submitted');
    console.log(`form data: ${JSON.stringify(this.create_alert_form.value)}`);
    let basinAlertLevelData: AlertAreaLevels[] = this.basinAlertLevelService.getAllBasinAlertLvlData();
    console.log(`onsubmit form data: ${JSON.stringify(basinAlertLevelData)}`)
    // {"alert_description":"sdfsdf","alert_status":"active","meteorologicalDataEditor":"<p>sdfsf</p>","hydrologicalDataEditor":"<p>sdfsf</p>"}
    let new_alert: AlertCreate = {
      alert_description: this.create_alert_form.value.alert_description,
      alert_status: this.create_alert_form.value.alert_status,
      alert_hydro_conditions: this.create_alert_form.value.hydrologicalDataEditor,
      alert_meteorological_conditions: this.create_alert_form.value.meteorologicalDataEditor,
      additional_information: this.create_alert_form.value.additionalInformationDataEditor,
      alert_links: basinAlertLevelData,
      // should get this from the id token
      author_name: this.authzService.payload.display_name
    }
    this.alertService.addAlert(new_alert).subscribe((data) => {
      console.log(`data from post: ${JSON.stringify(data)}`);
      // this.alert_data = data.alert_id;
      this.router.navigate(['/alert', data.alert_id]);
    });
  }

  resetForm() {
    console.log("reset form")
    this.create_alert_form.get('alert_description')!.reset();
    this.create_alert_form.get('meteorologicalDataEditor')!.reset();
    this.create_alert_form.get('hydrologicalDataEditor')!.reset();
    this.create_alert_form.get('additionalInformationDataEditor')!.reset();
    this.create_alert_form.get('alert_status')!.reset();
  }

}
