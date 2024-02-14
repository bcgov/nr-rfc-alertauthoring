import { Component, Input, OnInit } from '@angular/core';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { CommonModule } from '@angular/common';
import { FormGroup, FormBuilder, FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AlertAreaLevels } from '../../alert';

import {MatTableModule} from '@angular/material/table';

export interface BasinAlertLevels {
  id: number;
  basin_name: string;
  alert_level: string;
}


@Component({
  selector: 'app-view-basin-level',
  standalone: true,
  imports: [MatInputModule, MatFormFieldModule, CommonModule, FormsModule, ReactiveFormsModule, MatTableModule],
  templateUrl: './view-basin-level.component.html',
  styleUrl: './view-basin-level.component.css'
})
export class ViewBasinLevelComponent implements OnInit{
  @Input() basin_level_list!: AlertAreaLevels[] | undefined;
  table_data!: BasinAlertLevels[];
  basin_level_group: FormGroup;
  column_names: string[] = ['basin_name', 'alert_level'];

  constructor(private formBuilder: FormBuilder) {
    this.basin_level_group = this.formBuilder.group({
      basin_id: '',
      basin_name: '',
      basin_level: '',
      last_updated_time: ''
    });
    
   }

  ngOnInit(): void {
    
    console.log(`this basin is: ${JSON.stringify(this.basin_level_list)}`);
    console.log(`type of data is: ${typeof(this.basin_level_list)}`);
    this.table_data = this.get_table_data();
  }

  get_table_data() {
    let table_data = [];
    for (let i = 0; i < this.basin_level_list!.length; i++) {
      let basin_name = this.basin_level_list![i].basin.basin_name
      let alert_level = this.basin_level_list![i].alert_level.alert_level;
      table_data.push({'id': i + 1, 'basin_name': basin_name, 'alert_level': alert_level});
    }
    console.log(`table data is: ${JSON.stringify(table_data)}`);
    return table_data;
  }


}
