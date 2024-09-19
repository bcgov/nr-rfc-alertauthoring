import { Component, OnInit, AfterViewInit, ViewChild, ElementRef, Input } from '@angular/core';
import { Map, map, tileLayer, popup, Control, DomUtil } from 'leaflet';
import { FeatureLayer } from "esri-leaflet";
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
  basins_fl!: FeatureLayer;
  basinStyles: any = {};

  mapUtil = new MapUtil();
  mapElementRef: ElementRef = null!;
  public _map!: Map;

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
    if (this.basins_fl != undefined) {
      // indicates the map has loaded, possibly after the alert levels have been loaded
      this.basins_fl.setStyle(this.styleMap);
    }

  }

  ngAfterViewInit() {
    this.initializeMap();
    this.basins_fl.setStyle(this.styleMap);
  }

  styleMap = (feature: any) : any => {
    // read the data from the basin-lvl-data service.
    console.log(`styleMap: feature is: ${JSON.stringify(feature.properties.Major_Basin)}`);
    console.log(`styleMap: basins are: ${JSON.stringify(this.basins)}`);
    let style: MapStyle = { color: "blue", weight: 2 };
    if (this.basins.includes(feature.properties.Major_Basin)) {
      let color = this.basinStyles[feature.properties.Major_Basin];
      console.log(`color is: ${color}`);
      style = { color: color, weight: 2, opacity: 1}
      style.fill = color;
      style.stroke = color;
    }
    console.log(`Style for basin: ${feature.properties.Major_Basin} is: ${JSON.stringify(style)}`);
    return style
  }

  basin_lvl_lu_func = (basin_name: string) : string => {
    let alert_level = this.alert_levels_list[this.basins.indexOf(basin_name)];
    return alert_level;
  }

  private initializeMap() {
    console.log("init map: " + JSON.stringify(this._map) + '-' + this._map);
    this._map = this.mapUtil.getMapObj(this._map);
    let legend = this.mapUtil.defineLegend();
    legend.addTo(this._map);
    this.basins_fl = this.mapUtil.addBasins(this.styleMap)
    this.basins_fl.addTo(this._map);
    this.mapUtil.addBasinPopup(this._map, this.basins_fl, this.basin_lvl_lu_func);
    console.log("map has been initialized");
  }
}

interface MapStyle {
  color: string;
  weight: number;
  fill?: string;
  stroke?: string;
  opacity?: number;
}