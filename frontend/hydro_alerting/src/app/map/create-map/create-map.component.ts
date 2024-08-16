import { Component, OnInit, AfterViewInit } from '@angular/core';
import { Map, map, popup, Control, DomUtil, Layer, LatLng } from 'leaflet';
import { featureLayer, FeatureLayer } from "esri-leaflet";


import { MapUtil } from "../map_defaults";
import { AlertAreaLevels } from '../../types/alert';


@Component({
  selector: 'app-create-map',
  standalone: true,
  imports: [],
  templateUrl: './create-map.component.html',
  styleUrl: './create-map.component.css'
})
export class CreateMapComponent implements OnInit, AfterViewInit {

  public _map!: Map
  mapUtil = new MapUtil();
  basins_fl!: FeatureLayer;
  latlng!: LatLng;
  current_basin!: any;


  ngAfterViewInit(): void {
    this.initializeMap();
  }
  ngOnInit(): void {
    
  }

  private initializeMap() {

    let container: any = DomUtil.get("map");
  
    
    if (JSON.stringify(container) != JSON.stringify({})) {
      // prevents the partial loads of the map from erroring with
      // with the map already being defined error
      DomUtil.empty(container);
      container.outerHTML = "";
      container.remove();
    }

    console.log("init map: " + JSON.stringify(this._map) + '-' + this._map);
    this._map = this.mapUtil.getMapObj(this._map);
    let legend = this.mapUtil.defineLegend(this._map);
    legend.addTo(this._map);

    // get latlong from every click event
    this._map.on('click', (e: any) => {
      this.latlng = e.latlng;
      console.log("latlng: " + this.latlng);
    });

    this.basins_fl = this.mapUtil.addBasins(this._map, this.styleMap)
    this.basins_fl.addTo(this._map);

    // get feature layer from point
    // get current basin
    this.basins_fl.on('click', (e) => {
        console.log(e.layer.feature.properties.Major_Basin);
        this.current_basin = e.layer.feature;
    });

    this.addBasinAlertLevelSetterPopup(this._map, this.basins_fl, this.basin_lvl_lu_func);
    this._map.on('popupopen', this.popupevent.bind(this));
  }

  popupevent(layer: any) {
    console.log("popup open event" + layer);
    console.log("event type: " + layer.type);
    console.log("event sourceTarget from: " + layer.originalEvent);
    console.log(layer);
    const popupContent = layer.popup.getContent();
    const saveButton = document.getElementById('saveAlertLevel');
    
    if (saveButton) {
      saveButton.addEventListener('click', () => this.setAlertLevel(layer));
      console.log("added save button event listener, button..." + saveButton);
    }
  


  }

    // a) need to get the alert level options... could get passed into parent 
    //    component as an input, or could get from a service
    //
    // b) ideally should add in functionality to prevent a basin from being 
    //    added twice.
    addBasinAlertLevelSetterPopup(map: Map, basins_fl: FeatureLayer, basin_level_func: CallableFunction) {
      // a) need to get the alert level options... could get passed into parent 
      //    component as an input, or could get from a service
      //
      // b) ideally should add in functionality to prevent a basin from being 
      //    added twice.
      
      basins_fl.on('click', (e: any): any => {
        let alert_level = basin_level_func(e.layer.feature.properties.Major_Basin);
        if (!alert_level) {
          alert_level = "None";
        }
        alert_level = 'Alert Level: <b>' + alert_level + '</b>'
  
        var myPopup = popup()
          .setLatLng(e.latlng)
          .setContent(this.mapUtil.dropdown);
        myPopup.openOn(map)
  });
}

  styleMap = (feature: any) : any => {
    console.log(`feature is: ${JSON.stringify(feature.properties.Major_Basin)}`);
    return { color: "blue", weight: 2 };
  }

  basin_lvl_lu_func = (basin_name: string) : string => {
    return "None";
  }

  public setAlertLevel(layer: any) {
    console.log("setting alert level...");
    const dropdonwValue = DomUtil.get('ddlViewBy');
    let alert_level = "None";
    if (dropdonwValue) {
      const selectElem = dropdonwValue as HTMLSelectElement;
      alert_level = selectElem.options[selectElem.selectedIndex].value;
    }
    console.log("basin: " + this.current_basin.properties.Major_Basin);
    this.current_basin.style.color = 'red';
    console.log("alert level: " + alert_level);
    this._map.closePopup()
    // TODO: change color of underlying layer

  }



}
