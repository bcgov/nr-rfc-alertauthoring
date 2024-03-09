import { Component, EventEmitter, OnInit, Output, Input, AfterViewInit } from '@angular/core';
import { Observable } from 'rxjs';
import { Basin } from '../../types/basin';
import { map } from 'rxjs/operators';
import {  FormBuilder, FormGroup, FormsModule,  ReactiveFormsModule } from '@angular/forms';

import {MatInputModule} from '@angular/material/input';
import {MatSelectModule, MatSelectChange} from '@angular/material/select';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatButtonModule} from '@angular/material/button';

import { CommonModule,  } from '@angular/common';
import { AlertAreaLevels } from '../../types/alert';
// TODO: move functionality of basin service into the BasinLvlDataService so we 
//       can keep track of what basins already have alerts associated with them
import { BasinService } from '../../services/basin.service';
import { BasinLvlDataService} from '../../services/basin-lvl-data.service';


import {BasinLvl} from '../../types/basin-lvl';

@Component({
  selector: 'app-basin-alertlvl',
  standalone: true,
  imports: [
    MatInputModule,
    MatFormFieldModule,
    MatSelectModule,
    MatButtonModule,
    FormsModule,
    ReactiveFormsModule,
    CommonModule,
  ],
  
  templateUrl: './basin-alertlvl.component.html',
  styleUrl: './basin-alertlvl.component.css'
})
export class BasinAlertlvlComponent implements AfterViewInit {
  basins!: Observable<Basin[]>;
  basin_alertlvl_form: FormGroup;

  // this data comes in via inputs, and it communicated back to the dynamic component
  // service via the service basinDataSvc
  @Input() basin_name!: string;
  @Input() alert_level!: string;
  @Input() component_id!: number;
  
  constructor(
    private formBuilder: FormBuilder,
    private basinService: BasinService,
    private basinDataSvc: BasinLvlDataService,
    ) {
      console.log(`comp init... basin_name: ${this.basin_name}, alert_level: ${this.alert_level}`)
      this.basin_alertlvl_form = this.formBuilder.group({
        basin_name: [this.basin_name,],
        alert_level: [this.alert_level,],
      }); 
  }

  // ngOnInit(): void {
  ngAfterViewInit(): void {
    console.log("after view init called basin is ", this.basin_name, ' ', this.alert_level)
    this.basins = this.basinService.getBasins().pipe(map((basins) => {
      return basins.map((basin: Basin) => {
        return basin;
      })
    }));
    this.basin_alertlvl_form = this.formBuilder.group({
      basin_name: [this.basin_name,],
      alert_level: [this.alert_level,],
    }); 

  }

  alertLvlChange(event: MatSelectChange) {
    // called when the alert level is changed
    console.log(`event value: ${event.value}`);
    this.basinDataSvc.addAlertLvl(event.value, this.component_id);
    this.basin_alertlvl_form = this.formBuilder.group({
      basin_name: [this.basin_name,],
      alert_level: [this.alert_level,],
    }); 

  }

  basinChange(event: MatSelectChange) {
    // called when the basin selection is changed
    console.log(`event value: ${event.value}`);
    // this.basin_alertlvl_form.controls['alert_level'].setValue(event.value);
    this.basinDataSvc.addBasin(event.value, this.component_id);
  }

  onDeleteElement() {
    // removes the dynamic basin/alertlvl component from the view
    console.log(`delete called, component_id: ${this.component_id}`);
    console.log(`event data: ${JSON.stringify(this.basin_alertlvl_form.value)}`);
    let basin_name = this.basin_alertlvl_form.value.basin_name;
    console.log(`basin_name before call: ${basin_name}`);
    let event_descr: BasinLvl = {
      basin_name: basin_name,
      alert_level: this.basin_alertlvl_form.value.alert_level,
      event_type: 'delete'
    };
    this.basinDataSvc.deleteComponent(this.component_id);
    console.log('emitted delete event');
  }

  update_component(basin_name: string, alert_level: string){
    // updates the component with the new data
    console.log(`update_component called, basin_name: ${basin_name}, alert_level: ${alert_level}`);
    this.basin_alertlvl_form.controls['basin_name'].setValue(basin_name);
    this.basin_alertlvl_form.controls['alert_level'].setValue(alert_level);
  }

}