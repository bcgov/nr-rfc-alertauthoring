import { BehaviorSubject, Observable, ReplaySubject } from 'rxjs';
import {Injectable, Type} from '@angular/core';
import { BasinLvl } from '../types/basin-lvl';
import { BasinAlertlvlComponent } from '../basin-alertlvl/basin-alertlvl.component';

// service is used to keep track of what basins have already been alocated
// and which are available for allocation

@Injectable({ providedIn: 'root' })
export class BasinLvlDataService {

  // will serve as a central store to the basin/alert-lvl data
  // and components that are displayed by the basin-lvl component
  all_basin_level_component = <any>[];
  
  dataSubject: BehaviorSubject<any[]>;
  all_basin_level_component_obs!: Observable<any[]>;

  // dataSubject: BehaviorSubject<string> = new BehaviorSubject<string>(1);
  allocatedBasins: string[] = [];

  // componentService: BasinLvlComponentService;
  

  constructor(private componentService: BasinLvlComponentService) {
    // this.all_basin_level_component_obs$ = this.dataSubject$.asObservable();
    // add a value to the subject
    console.log("constructor called")
    // this.componentService = new BasinLvlComponentService();
    this.dataSubject = new BehaviorSubject<any>(null);
    this.all_basin_level_component_obs = this.dataSubject.asObservable();
    this.dataSubject.next([this.getDefaultBasinLvls()]);
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
        component.inputs.alert_level = alert_level;
      }
    });
  }

  /**
   * 
   * @returns a new dynamic basin level component and the data associated with it
   */
  addNewBasinAlertSelector() {
    return this.componentService.addComponentBlankComponent();
  }

  getAllComponents() {
    console.log(`all basin level components: ${JSON.stringify(this.componentService.components)}`);
    return this.componentService.components;
  }


  setBasinAlertlvlComponentData(data: any) {

  }


  getDefaultBasinLvls() {
    return this.componentService.getDefaultComponents();
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

  private default_empty_component  = {
    component: BasinAlertlvlComponent,
    inputs: { basin_name: '', alert_level: '', component_id: 1 }
  }

  getDefaultComponents()  {
    this.addComponentBlankComponent();
    console.log(`defaultComponents: ${JSON.stringify(this.components)}`);
    return this.components as {component: Type<any>, inputs: Record<string, unknown>}[];
  }

  getComponents() {
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
    let cur_comp = 
    {
      component: BasinAlertlvlComponent,
      inputs: { basin_name: '', alert_level: '', component_id: comp_id }
    }
    // let cur_comp = this.default_empty_component;
    this.components.push(cur_comp);
    console.log(`cur_comp: ${JSON.stringify(cur_comp)}`);
    console.log(`default comp: ${JSON.stringify(this.default_empty_component)}`);
    console.log(`all comps: ${JSON.stringify(this.components)}`)
  }

}