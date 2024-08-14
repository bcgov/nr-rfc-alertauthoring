import { Component, OnInit, AfterViewInit, Input, ElementRef, ViewChild } from '@angular/core';
import { Alert, AlertAreaLevels } from '../../types/alert';
import { Map, map, tileLayer, popup, Control, DomUtil } from 'leaflet';
import { Observable } from 'rxjs';
import { MapUtil } from "../map_defaults";
import {AlertCreate} from '../../types/alert';
import { DOCUMENT } from '@angular/common'; 
import { FeatureLayer } from 'esri-leaflet';


@Component({
  selector: 'app-ovrview-map',
  standalone: true,
  imports: [],
  templateUrl: './ovrview-map.component.html',
  styleUrl: './ovrview-map.component.css'
})
export class OvrviewMapComponent implements OnInit, AfterViewInit {
  @Input() alertLevels!: Observable<Alert[]>;
  @ViewChild('map', { static: false }) public mapContainer!: ElementRef;
  // @ViewChild('mydiv', { static: false }) public mydiv: ElementRef;


  mapUtil = new MapUtil();
  mapElementRef: ElementRef = null!;
  mapElem: any;

  public _map!: Map;
  basins: string[] = [];
  alert_levels: string[] = [];
  basins_fl!: FeatureLayer;

  // # alertLevels
  ngAfterViewInit() {
    this.initMap();
  }

  constructor() {
    
  }

  ngOnInit(): void {
    console.log("Doing the subscription to the basin / alert levels")
    this.readBasinAlertLevels();
  }

  private readBasinAlertLevels(): void {
    console.log(`basin info: ${this.basins}`)
    if (this.basins.length <= 0) {
      this.alertLevels.subscribe((alertCreate: AlertCreate[]) => {
        /// getting the data from the observable
        for (let i = 0; i < alertCreate.length; i++) {
          let alert: AlertCreate = alertCreate[i];
          if (alert.alert_links) {
            for (let j = 0; j < alert.alert_links.length; j++) {
              console.log("got basin: " + alert.alert_links[j].basin.basin_name);
              this.basins.push(alert.alert_links[j].basin.basin_name);
              this.alert_levels.push(alert.alert_links[j].alert_level.alert_level);
            }
          }
        }
        if (this.basins_fl != undefined) {
          // indicates the map has loaded, possibly after the alert levels have been loaded
          this.basins_fl.setStyle(this.styleMap);
        }
    });
    }
  }


  private initMap(): void {
    // when toggling between specific alerts and overview map, the map container
    // for the overview map was erroring out with the error: 
    // "Map container is already initialized"  Manually setting the outerHTML
    // seems to resolve this issue.
    //this.readBasinAlertLevels();
    let container: any = DomUtil.get("map");
  
    
    if (JSON.stringify(container) != JSON.stringify({})) {
      DomUtil.empty(container);
      // this is what works to remove the map container from the DOM, when the 
      // page gets a partial reload, without this code will eventually get a 
      // "Map container is already initialized" error
      container.outerHTML = "";
      container.remove();
    }

    this._map = this.mapUtil.getMapObj(this._map);
    let legend = this.mapUtil.defineLegend(this._map);
    legend.addTo(this._map);
    this.basins_fl = this.mapUtil.addBasins(this._map, this.styleMap)
    this.basins_fl.addTo(this._map);

    this.mapUtil.addBasinPopup(this._map, this.basins_fl, this.basin_lvl_lu_func);
  }

  styleMap = (feature: any): any => {
    console.log(`feature is: ${JSON.stringify(feature.properties.Major_Basin)}`);
    let current_basin = feature.properties.Major_Basin;
    if (this.basins.includes(current_basin)) {
      let color = this.mapUtil.color_lookup[this.alert_levels[this.basins.indexOf(current_basin)]];
      console.log(`color is: ${color}`);
      return { color: color, weight: 2 };
    } else {
      return { color: "blue", weight: 2 };
    }
  }

  basin_lvl_lu_func = (basin_name: string): string => {
    let alert_level = this.alert_levels[this.basins.indexOf(basin_name)];
    return alert_level;
  }

}
