import { BehaviorSubject, Observable } from 'rxjs';
import {ChangeDetectorRef, Injectable, Type, AfterViewInit} from '@angular/core';
import { BasinLvlDynamicComponent } from '../types/basin-lvl';
import { BasinAlertlvlComponent } from '../basin-alerts/basin-alertlvl/basin-alertlvl.component';
import {AlertAreaLevels} from '../types/alert';

// service is used to keep track of what basins have already been alocated
// and which are available for allocation

@Injectable({ providedIn: 'root' })
export class BasinLvlDataService {

  // will serve as a central store to the basin/alert-lvl data
  // and components that are displayed by the basin-lvl component
  all_basin_level_component : BasinLvlDynamicComponent[] = [];
  
  dataSubject: BehaviorSubject<any[]>;
  all_basin_level_component_obs!: Observable<any[]>;

  // dataSubject: BehaviorSubject<string> = new BehaviorSubject<string>(1);
  allocatedBasins: string[] = [];  

  constructor(
      private componentService: BasinLvlComponentService) {

    // add a value to the subject
    console.log("constructor called")
    // this.componentService = new BasinLvlComponentService();
    this.dataSubject = new BehaviorSubject<any>(null);
    this.all_basin_level_component_obs = this.dataSubject.asObservable();
  }

  reset() {
    this.componentService.reset();
  }

  addBasin(basin_name: string, component_id: number) {
    this.allocatedBasins.push(basin_name);
    this.componentService.components.forEach((component: any) => {
      if (component.inputs.component_id === component_id) {
        component.inputs.basin_name = basin_name;
      }
    });
  }

  addAlertLvl(alert_level: string, component_id: number) {
    this.componentService.components.forEach((component: any) => {
      if (component.inputs.component_id === component_id) {
        component.inputs.alert_level_name = alert_level;
      }
    });
  }

  getAllBasinAlertLvlData() : AlertAreaLevels[] {
    console.log("getting all basin alert level data");
    let basin_alert_lvl_data: AlertAreaLevels[] = [];
    this.componentService.components.forEach((component: any) => {
      console.log(`component: ${JSON.stringify(component)}`);
      basin_alert_lvl_data.push({
        "basin": {
          "basin_name": component.inputs.basin_name
        },
        "alert_level": {
          "alert_level": component.inputs.alert_level_name
        }
      });
    });
    return basin_alert_lvl_data;
  }

  /**
   * 
   * @returns a new dynamic basin level component and the data associated with it
   */
  addNewBasinAlertSelector() {
     this.componentService.addComponentBlankComponent();
  }

  getAllComponents() {
    console.log(`all basin level components: ${JSON.stringify(this.componentService.components)}`);
    return this.componentService.components;
  }

  setBasinAlertlvlComponentData(alertAreaLevels: AlertAreaLevels[] | undefined) {
    if (alertAreaLevels) {
      // overwrite existing components
      this.componentService.reset();
      let comp_id = 1;
      alertAreaLevels.forEach((alertAreaLevel: AlertAreaLevels) => {
        console.log(`alertlevel data: ${JSON.stringify(alertAreaLevel)}`)
        let cur_comp = {
          component: BasinAlertlvlComponent,
          inputs: { 
            basin_name: alertAreaLevel.basin.basin_name, 
            alert_level_name: alertAreaLevel.alert_level.alert_level, 
            component_id: comp_id }
        }
        console.log(`cur_comp populated with: ${JSON.stringify(cur_comp)}`);
        this.componentService.components.push(cur_comp);
        comp_id = comp_id + 1;
        // this.dataSubject.next([cur_comp]);
        // this.cdr.detectChanges();
      });
    }
  }


  /** Removes a basin/alert level component from the form */
  deleteComponent(component_id: number) {
    this.componentService.deleteComponent(component_id);
  }


  allocateBasin(basin_name: string) {
    // potentially the method that will be used to add a new basin to the 
    // already allocated list
    this.allocatedBasins.push(basin_name);
  }

}


@Injectable({ providedIn: 'root' })
export class BasinLvlComponentService  {
  // tighten up the typing here
  components = <any>[];

  private default_empty_component: BasinLvlDynamicComponent  = {
    component: BasinAlertlvlComponent,
    inputs: { basin_name: '', alert_level_name: '', component_id: 1 }
  }

  reset() {
    this.components = [];
  }

  getComponents() : BasinLvlDynamicComponent[] {
    return this.components;
  }

  deleteComponent(component_id: number) {
    // working
    console.log(`delete called, component_id: ${component_id}`);
    for (var i = 0; i < this.components.length; i++) {
      console.log(`iterated value: ${JSON.stringify(this.components[i])}`);
      if (this.components[i].inputs.component_id === component_id) {
        console.log(`deleting component: ${JSON.stringify(this.components[i])}`);
        this.components.splice(i, 1);
        break;
      }
    }
  }

  addComponentBlankComponent() {
    let comp_id = this.components.length + 1;
    //let cur_comp = JSON.parse(JSON.stringify(this.default_empty_component));
    let cur_comp : BasinLvlDynamicComponent = 
    {
      component: BasinAlertlvlComponent,
      inputs: { basin_name: '', alert_level_name: '', component_id: comp_id }
    }
    // let cur_comp = this.default_empty_component;
    this.components.push(cur_comp);
    console.log(`cur_comp: ${JSON.stringify(cur_comp)}`);
    console.log(`default comp: ${JSON.stringify(this.default_empty_component)}`);
    console.log(`all comps: ${JSON.stringify(this.components)}`)
  }

}