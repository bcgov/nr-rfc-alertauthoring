import { BehaviorSubject, Observable } from 'rxjs';
import { ChangeDetectorRef, Injectable, Type, AfterViewInit, computed, signal, WritableSignal, Signal, effect } from '@angular/core';
import { BasinLvlDynamicComponent } from '../types/basin-lvl';
import { BasinAlertlvlComponent } from '../basin-alerts/basin-alertlvl/basin-alertlvl.component';
import { AlertAreaLevels } from '../types/alert';
import { MapUtil } from '../map/map_defaults';

// service is used to keep track of what basins have already been alocated
// and which are available for allocation

@Injectable({ providedIn: 'root' })
export class BasinLvlDataService {

  // will serve as a central store to the basin/alert-lvl data
  // and components that are displayed by the basin-lvl component
  all_basin_level_component: BasinLvlDynamicComponent[] = [];

  dataSubject: BehaviorSubject<any[]>;
  allocatedBasins: string[] = [];
  mapUtil = new MapUtil();

  // default styles, and the signal that will be used to update the map
  default_styles = {'None': {'style': {color: '#3388ff', weight: 2, stroke: '#3388ff', 'fill-opacity': .2, fill: '#3388ff', 'stroke-opacity': 1}}};
  basinStyles: WritableSignal<BasinStyles> = signal<BasinStyles>(this.default_styles);

  refreshMapCallbackFunction: any|null = null;
  refreshMethod: any|null = null;
  refreshMethod2: any|null = null; // attempt to bind the callback to the object

  // test computed value signal, eventually delete
  reportSignal: Signal<any> = computed(() => {
    console.log("computed: basinStyle change detected");
    let styles = this.basinStyles();
    let basins = Object.keys(styles);
    console.log(`computed basin names: ${basins}`);
    return basins
  });

  constructor(
    private componentService: BasinLvlComponentService) {
      effect(() => {
        // monitoring for signal event/changes
        console.log("effect: called");
        let styles = this.basinStyles();
        console.log(`The current count is: ${Object.keys(this.basinStyles()).length}`);
      });
    console.log("constructor called")
    this.dataSubject = new BehaviorSubject<any>(null);
  }

  reset() {
    this.componentService.reset();
  }

  addStyle(basin_name: string, style: MapFeatureStyle, feature: any) {
    let styles = this.basinStyles();
    // forcing a deep copy results in a different object reference
    // which will then trigger the effect signal... this is a hack
    styles = structuredClone(styles);
    styles[basin_name] = style;
    styles[basin_name].feature = feature;
    this.basinStyles.set(styles);

    console.log(`the basin style: ${this.basinStyles()[basin_name].feature.id}`);
    // force effect to run for signal, only seems to run on update... 
    //this.basinStyles.update(x => ({ ...x, [basin_name]: style }));
    console.log(`added the basin: ${basin_name}`);
    console.log(`number of basins: ${Object.keys(this.basinStyles()).length}`);
  }

  getStyle(basin_name: string) :any {
    let basin_style = {}
    if (basin_name in this.basinStyles()) {
      basin_style = this.basinStyles()[basin_name];
    }
    return basin_style;
  }

  updateStyles(component_id: number) {
    let comp = this.componentService.getComponent(component_id);
    if (comp) {
      let basin_name = comp.inputs.basin_name;
      let alert_level = comp.inputs.alert_level_name;
      if (basin_name && alert_level) {
        // let color = 'black';
        let color = this.mapUtil.color_lookup[alert_level];
        let curStyles = this.basinStyles();
        // forcing a deep copy results in a different object reference
        // which will then trigger the effect signal... this is a hack
        curStyles = structuredClone(curStyles);
        curStyles[basin_name] = {feature: curStyles[basin_name].feature, style: {color: color, weight: 2}};

        console.log(`updated basin_name ${basin_name} with color: ${color}`);
        let style = {style: {color: color, weight: 2}};
        let feature = curStyles[basin_name].feature;
        this.basinStyles.set(curStyles);

        // currently not triggering the effect signal because the reference
        // hasn't changed... I don't know what to do to trigger the effect method
        // would be great if we could figure this out, then any time the data
        // changes we would could tie in an update to the map

        // this line will result in a trigger, but doesn't update the object properly
        // result is the feature property is getting removed.  Couldn't figure 
        // out how to using the spread operator to update the object properly
        //this.basinStyles.update(x => ({...x, [basin_name]: style}));        
      }
    }
  }

  /**
   * 
   * @param basin_name - input basin name
   * @param component_id - the id of the component who's basin is being assigned
   */
  addBasin(basin_name: string, component_id: number) {
    let alert_level = ''
    this.componentService.components.forEach((component: any) => {
      if (component.inputs.component_id === component_id) {
        component.inputs.basin_name = basin_name;
        this.updateStyles(component_id);
        alert_level = component.inputs.alert_level_name;
      }
    });
    // this.allocatedBasins.push(basin_name);
    this.addAllocatedBasin(basin_name);
    // if alert level is also populated then update the map
    if (alert_level) {
      this.updateMap(basin_name);
    }
  }

  /**
   * 
   * @param alert_level the input alert level to be set for the component
   * @param component_id the component id who's alert level is being set
   */
  addAlertLvl(alert_level: string, component_id: number) {
    let basin = '';
    this.componentService.components.forEach((component: any) => {
      if (component.inputs.component_id === component_id) {
        component.inputs.alert_level_name = alert_level;
        this.updateStyles(component_id);
        basin = component.inputs.basin_name;
      }
    });
    // if basin is also populated the update the map
    if (basin) {
      this.updateMap(basin);
    }
  }    

  setMapUpdateCallback(callback: any, objRef: any) {
    // let callback 
    let style = this.basinStyles();
    console.log(`basin styles: ${JSON.stringify(style)}`);

    this.refreshMethod = callback.bind(objRef);

  }

  updateMap(basin_name: string) {
    console.log("updateMap called");
    console.log(`basin_name: ${basin_name}`);
    let style = this.basinStyles();
    console.log(`basin styles: ${JSON.stringify(style)}`);

    if (this.refreshMethod) {
      this.refreshMethod(basin_name, this);
    }

  }

  getAllBasinAlertLvlData() : AlertAreaLevels[] {
    console.log("getting all basin alert level data");
    let basin_alert_lvl_data: AlertAreaLevels[] = [];
    this.componentService.components.forEach((component: any) => {
      console.log(`component data: ${JSON.stringify(component)}`);
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
   * Adds a new unpopulated basin / alert level component to the form
   */
  addNewBasinAlertSelector() {
    this.componentService.addComponentBlankComponent();
  }

  /**
   * 
   * @returns all the components that have been added to the form
   */
  getAllComponents() :any[] {
    console.log(`all basin level components: ${JSON.stringify(this.componentService.components)}`);
    return this.componentService.components;
  }

  getComponentId(basin_name: string) : number | null {
    let cur_comp_id: number | null = null;
    for (const component of this.componentService.components) {
      if (component.inputs.basin_name === basin_name) {
        cur_comp_id = component.inputs.component_id;
        return cur_comp_id;
      }
    }
    return cur_comp_id;
  }

  getAlertLevel(basin_name: string) : string | null {
    let cur_alert_level: string | null = null;
    for (const component of this.componentService.components) {
      if (component.inputs.basin_name === basin_name) {
        cur_alert_level = component.inputs.alert_level_name;
        return cur_alert_level;
      }
    }
    return cur_alert_level;
  }

  /** 
  * 
  * @returns the id of the first component that does not have any data
  *          assigned to it.  If there isn't any empty / non populated
  *          components in the view, then a new one is added to the form
  *          and its id is returned
  */
  getEmptyComponentId(): number | null {
    let cur_comp_id: number | null = null;
    for (const component of this.componentService.components) {
      if (component.inputs.basin_name === '' && component.inputs.alert_level_name === '') {
        cur_comp_id = component.inputs.component_id;
        return cur_comp_id;
      }
    }
    if (cur_comp_id === null) {
      this.addNewBasinAlertSelector();
      cur_comp_id = this.getEmptyComponentId();
    }
    return cur_comp_id;
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
            component_id: comp_id
          }
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
    let comp = this.componentService.getComponent(component_id);
    let basin_name = '';
    let alert_level = '';
    if (comp) {
      basin_name = comp.inputs.basin_name;
      alert_level = comp.inputs.alert_level_name;
      this.removeAllocatedBasin(basin_name);
      // need to update the map now

    }
    this.componentService.deleteComponent(component_id);
    // this.componentService.components.forEach((component: any) => {

    // }
    // TODO: set the map back to default style

    // may have to do something like this to get the changes to save
    //     styles = structuredClone(styles);
    // styles[basin_name] = style;
    // styles[basin_name].feature = feature;
    // this.basinStyles.set(styles);

    let styles = this.basinStyles()
    if (basin_name in styles) {
      styles[basin_name].style = styles['None'].style;
      this.basinStyles.set(styles);
    }
    this.updateMap(basin_name);
  }

  getAllocatedBasins() : string[] {
    // let compData = this.getAllBasinAlertLvlData();
    // let basins: string[] = [];
    // compData.forEach((comp: any) => {
    //   basins.push(comp.basin.basin_name);
    // });
    // return basins;
    return this.allocatedBasins;
  }

  addAllocatedBasin(basin_name: string) {
    // potentially the method that will be used to add a new basin to the 
    // already allocated list
    if (!this.allocatedBasins.includes(basin_name)) {
      console.log("adding basin to allocated list: " + basin_name);
      this.allocatedBasins.push(basin_name);
      console.log("allocated list: " + this.allocatedBasins);
    }
  }

  removeAllocatedBasin(basin_name: string) {
    // potentially the method that will be used to remove a basin from the 
    // already allocated list
    console.log("removing basin from allocated list: " + basin_name);
    this.allocatedBasins = this.allocatedBasins.filter((basin) => {
      return basin !== basin_name;
    });
  }

  isBasinAllocated(basin_name: string) {
    return this.allocatedBasins.includes(basin_name);
  }

}


@Injectable({ providedIn: 'root' })
export class BasinLvlComponentService {
  // tighten up the typing here
  components = <any>[];

  private default_empty_component: BasinLvlDynamicComponent = {
    component: BasinAlertlvlComponent,
    inputs: { basin_name: '', alert_level_name: '', component_id: 1 }
  }

  reset() {
    this.components = [];
  }

  getComponents(): BasinLvlDynamicComponent[] {
    return this.components;
  }

  getComponent(component_id: number): BasinLvlDynamicComponent | null {
    for (const component of this.components) {
      if (component.inputs.component_id === component_id) {
        return component;
      }
    }
    return null;
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

    let comp_id = this.getMaxComponentId() + 1;
    let cur_comp: BasinLvlDynamicComponent =
    {
      component: BasinAlertlvlComponent,
      inputs: { basin_name: '', alert_level_name: '', component_id: comp_id }
    }
    this.components.push(cur_comp);
    console.log(`cur_comp: ${JSON.stringify(cur_comp)}`);
    console.log(`default comp: ${JSON.stringify(this.default_empty_component)}`);
    console.log(`all comps: ${JSON.stringify(this.components)}`)
  }

  private getMaxComponentId() {
    let max_id = 0;
    for (const component of this.components) {
      if (component.inputs.component_id > max_id) {
        max_id = component.inputs.component_id;
      }
    }
    return max_id;
  }

}

interface BasinStyles {
  [key: string]: MapFeatureStyle;
}

interface MapFeatureStyle {
  feature?: any;
  style: {
    color: string;
    weight?: number;
    stroke?: string;
    opacity?: number;
    fill?: string;
    'stroke-opacity'?: number; // Optional property
    'fill-opacity'?: number; // Optional property
  };
}


