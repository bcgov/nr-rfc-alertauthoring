import { Component, OnInit, AfterViewInit, inject, computed, effect } from '@angular/core';
import { Map, popup, Control, DomUtil, Layer, LatLng, Popup } from 'leaflet';
import { featureLayer, FeatureLayer } from "esri-leaflet";


import { MapUtil } from "../map_defaults";
import { BasinLvlDataService } from '../../services/basin-lvl-data.service';
import { Basin } from '../../types/basin';
import { AlertAreaLevels, AlertLevel } from '../../types/alert';

@Component({
  selector: 'app-create-map',
  standalone: true,
  imports: [],
  //providers: [], //BasinLvlDataService
  templateUrl: './create-map.component.html',
  styleUrl: './create-map.component.css'
})
export class CreateMapComponent implements OnInit, AfterViewInit {

  public _map!: Map
  mapUtil = new MapUtil();
  basins_fl!: FeatureLayer;
  latlng!: LatLng;
  current_basin!: any;
  popup!: Popup;

  constructor(private basinLvlDataService: BasinLvlDataService) {
    this.refreshFeature.bind(this);
    this.basinLvlDataService.setMapUpdateCallback(this.refreshFeature, this);
   }

  ngAfterViewInit(): void {
    this.initializeMap();

    // refresh the data in the callback
    this.basinLvlDataService.setMapUpdateCallback(this.refreshFeature, this)
  }

  ngOnInit(): void { }

  private initializeMap() {

    // page init... clearing out stale map container
    let container: any = DomUtil.get("map");
    if (JSON.stringify(container) != JSON.stringify({})) {
      // prevents the partial loads of the map from erroring with
      // with the map already being defined error
      DomUtil.empty(container);
      container.outerHTML = "";
      container.remove();
    }

    // Create map
    console.log("init map: " + JSON.stringify(this._map) + '-' + this._map);
    this._map = this.mapUtil.getMapObj(this._map);

    // Create legend
    let legend = this.mapUtil.defineLegend();
    legend.addTo(this._map);

    // add basin feature layer to map
    this.basins_fl = this.mapUtil.addBasinsEditCreate(this.styleMap, this.basinLvlDataService, this)
    this.basins_fl.addTo(this._map);

    // get feature layer from point
    // get current basin
    this.basins_fl.on('click', (e) => {
      console.log(e.layer.feature.properties.Major_Basin);
      this.current_basin = e.layer.feature;
      this.onMapClick(e)
    });

  }

  /**
   * when map click takes place will create a popup with the basin name in it, 
   * and a dropdown to select the alert level for the basin
   * 
   * @param e - a map click event on the basin_fl layer
   * 
   */
  public onMapClick(e: any) {
    console.log("map click event");
    console.log("map click event current basin: " + JSON.stringify(this.current_basin));

    let curEvent = e;
    // in case the popup has not been created yet
    if (this.popup === undefined) {
      console.log("popup is undefined");
      this.popup = popup();
    }
    this.popup
      .setLatLng(e.latlng)
      .setContent(this.mapUtil.getPopupContent(e.layer.feature.properties.Major_Basin))
      .openOn(this._map);

    setTimeout(() => {
      const saveButton = document.getElementById('saveAlertLevel');
      console.log("added save button event listener, button..." + saveButton);
      if (saveButton) {
        saveButton.addEventListener('click', (e) => this.mapUtil.setAlertLevel(
          e,
          this.current_basin.properties.Major_Basin,
          this,
          curEvent));
      }
    }, 0);

    const dropdonwValue = DomUtil.get('ddlViewBy');

    // getting the basin name... below
    console.log(`basin is: ${e.layer.feature.properties.Major_Basin}`);
    // this.current_basin.style = { color: 'red', weight: 2 };
  }

  public refreshFeature(basin: string, classRef:any=null) {
    // redraw a the feature
    let style = null;
    if (classRef) {
      style = classRef.getStyle(basin);
    } else {
      style = this.basinLvlDataService.getStyle(basin);
    }
    console.log("feature id for Liard: " + style.feature.id);
    console.log("style for Liard: " + style.style);
    this.basins_fl.setFeatureStyle(style.feature.id, style.style)    
  }

  /**
  * 
  * @param feature 
  * @param basinLvlService 
  * @param color_lookup 
  * @returns 
  */
  public styleMap(feature: any, _basinLvlDataService: any, color_lookup: any, objRef: any): any {
    console.log(`feature is: ${JSON.stringify(feature.properties.Major_Basin)}`);

    // read the data from the basin-lvl-data service / signal.
    let styles = objRef.basinLvlDataService.basinStyles();

    // set the default style
    let style = styles['default']

    // check if a specific style has been defined for the current basin, and 
    // if so update the style variable to reflect basin specific style
    console.log("basins with styles: " + Object.keys(styles));
    if (feature.properties.Major_Basin in styles) {
      console.log("style found");
      style = styles[feature.properties.Major_Basin].style;
    }

    // updates the style lookup in the service, so that the non spatial basin / 
    // alert level selection widget can update the map (for this to work needs 
    // a reference to the 'feature' object)
    this.basinLvlDataService.addStyle(feature.properties.Major_Basin,
      { style: { color: "blue", weight: 2 } },
      feature)

    console.log("returned style is: " + JSON.stringify(style));
    return style;
  }

  /**
   *  A Utility/debugging function to list the properties of an object, 
   *  helping to understand what properties are available to be accessed, and 
   *  what different leaflet events are returning.
   * 
   * @param obj - the object to list the properties of
   * @param include_private - boolean to indicate if private properties should be included
   *                          in the returned properties
   * @returns a list of properties that belong to the object 'obj'
   */
  public listProperties(obj: any, include_private = false): string[] {
    var propList = [];
    if (Array.isArray(obj)) {
      obj = obj[0];
    }

    for (var propName in obj) {
      if (typeof (obj[propName]) != "undefined") {
        if (propName[0] != "_") {
          propList.push(propName);
        } else if (include_private == true) {
          propList.push(propName);
        }
      }
    }
    propList.sort();
    return propList;
  }


}
