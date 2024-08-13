import { Component, OnInit, AfterViewInit, ViewChild, ElementRef, Input } from '@angular/core';
import { Map, map, tileLayer, popup, Control, DomUtil } from 'leaflet';
import { featureLayer } from "esri-leaflet";
import { AlertAreaLevels } from '../../types/alert';
import { MapUtil } from "../map_defaults";

@Component({
  selector: 'app-view-map',
  standalone: true,
  imports: [],
  templateUrl: './view-map.component.html',
  styleUrl: './view-map.component.css'
})
export class ViewMapComponent implements OnInit, AfterViewInit {
  @Input() alertLevel?: AlertAreaLevels[];
  // @ViewChild('map')

  alert_levels: any = {};
  alert_levels_list: string[] = [];
  basins: string[] = [];
  basinStyles: any = {};

  mapUtil = new MapUtil();

  mapElementRef: ElementRef = null!;

  public _map!: Map

  constructor() {
  }

  ngOnInit() {
    if (this.alertLevel) {
      this.calcBasinAlertLevelLookups(this.alertLevel);
    }
  }

  private calcBasinAlertLevelLookups(alertLevel: AlertAreaLevels[]) {
    if (this.alertLevel) {
      for (let i = 0; i < this.alertLevel.length; i++) {
        this.alert_levels[this.alertLevel[i].basin.basin_name] = this.alertLevel[i].alert_level.alert_level;
        this.basins.push(this.alertLevel[i].basin.basin_name);
        this.alert_levels_list.push(this.alertLevel[i].alert_level.alert_level);
        this.basinStyles[this.alertLevel[i].basin.basin_name] = this.mapUtil.color_lookup[this.alertLevel[i].alert_level.alert_level];
      }
    }
  }

  ngAfterViewInit() {
    this.initializeMap();
  }

  styleMap = (feature: any) : any => {
    console.log(`feature is: ${JSON.stringify(feature.properties.Major_Basin)}`);
    console.log(`basins are: ${JSON.stringify(this.basins)}`);
    if (this.basins.includes(feature.properties.Major_Basin)) {
      console.log(`color is: ${this.basinStyles[feature.properties.Major_Basin]}`);
      return { color: this.basinStyles[feature.properties.Major_Basin], weight: 2 };
      // return { color: this.basinStyles[feature.properties.Major_Basin], weight: 2 };
    } else {
      return { color: "blue", weight: 2 };
    }
  }

  basin_lvl_lu_func = (basin_name: string) : string => {
    let alert_level = this.alert_levels_list[this.basins.indexOf(basin_name)];
    return alert_level;
  }

  private initializeMap() {
    console.log("init map: " + JSON.stringify(this._map) + '-' + this._map);
    this._map = this.mapUtil.getMapObj(this._map);
    let legend = this.mapUtil.defineLegend(this._map);
    legend.addTo(this._map);
    let basins_fl = this.mapUtil.addBasins(this._map, this.styleMap)
    basins_fl.addTo(this._map);

    this.mapUtil.addBasinPopup(this._map, basins_fl, this.basin_lvl_lu_func);
  }

}
