import { Component, EventEmitter, OnInit, Output, Input } from '@angular/core';
import { BasinService } from '../services/basin.service';
import { Observable } from 'rxjs';
import { Basin } from '../types/basin';
import { map } from 'rxjs/operators';
import {  FormBuilder, FormGroup, FormsModule,  ReactiveFormsModule } from '@angular/forms';

import {MatInputModule} from '@angular/material/input';
import {MatSelectModule} from '@angular/material/select';
import {MatFormFieldModule} from '@angular/material/form-field';
import {MatButtonModule} from '@angular/material/button';

import { CommonModule,  } from '@angular/common';
import { AlertAreaLevels } from '../types/alert';

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
    CommonModule],
  templateUrl: './basin-alertlvl.component.html',
  styleUrl: './basin-alertlvl.component.css'
})
export class BasinAlertlvlComponent implements OnInit {
  basins!: Observable<Basin[]>;
  basin_alertlvl_form: FormGroup;

  @Input() basin_name!: string;
  @Input() alert_level!: string;
  // work on figuring out type for values above if can get working

  // @Input() data!: any;
  
  @Output() delete: EventEmitter<any> = new EventEmitter();
  
  constructor(
    private formBuilder: FormBuilder,
    private basinService: BasinService) {
      
      this.basin_alertlvl_form = this.formBuilder.group({
        basin_name: ["",],
        alert_level: ["",],
      }); 
  }

  ngOnInit(): void {
    console.log(`basin name in init: ${this.basin_name!}`);
    this.basin_alertlvl_form.controls['basin_name'].setValue(this.basin_name);
    this.basin_alertlvl_form.controls['alert_level'].setValue(this.alert_level);
    this.basins = this.basinService.getBasins().pipe(map((basins) => {
      return basins.map((basin: Basin) => {
        return basin;
      })
    }));    
  }

  onDeleteElement() {
    console.log('calld onDeleteElement');
    console.log(`event data: ${JSON.stringify(this.basin_alertlvl_form.value)}`);
    this.delete.emit(this.basin_alertlvl_form.value);
    console.log('emitted delete event');
  }



}
