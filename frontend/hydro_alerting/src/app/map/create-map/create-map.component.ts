import { Component, OnInit, AfterViewInit } from '@angular/core';
import { Map, map, popup, Control, DomUtil, Layer, LatLng, Popup, Point } from 'leaflet';
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
  popup!: Popup;


  ngAfterViewInit(): void {
    this.initializeMap();
  }

  ngOnInit(): void { }

  private initializeMap() {

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
    let legend = this.mapUtil.defineLegend(this._map);
    legend.addTo(this._map);

    // add basin feature layer to map
    
    this.basins_fl = this.mapUtil.addBasins(this._map, this.styleMap)
    this.basins_fl.addTo(this._map);

    // get feature layer from point
    // get current basin
    this.basins_fl.on('click', (e) => {
      console.log(e.layer.feature.properties.Major_Basin);
      this.current_basin = e.layer.feature;
      this.onMapClick(e, this)
    });



    // didn't seem to bear any fruit!
    //this.addBasinAlertLevelSetterPopup(this._map, this.basins_fl, this.basin_lvl_lu_func);
    //this._map.on('popupopen', this.popupevent.bind(this));
  }

  public onMapClick(e: any, objref: any) {
    let curEvent = e;
    // in case the popup has not been created yet
    if (objref.popup === undefined) {
      console.log("popup is undefined");
      objref.popup = popup();
        // .setLatLng(e.latlng)
        // .setContent(objref.mapUtil.dropdown)
        // .openOn(objref._map);
    } 
    // else {
      objref.popup
        .setLatLng(e.latlng)
        //.setContent("You clicked the map at " + e.latlng.toString())
        .setContent(objref.mapUtil.dropdown)
        .openOn(objref._map);
    // }

    setTimeout(() => {
      const saveButton = document.getElementById('saveAlertLevel');
      console.log("added save button event listener, button..." + saveButton);
      if (saveButton) {
        saveButton.addEventListener('click', (e) => objref.mapUtil.setAlertLevel(e, this.current_basin.properties.Major_Basin, objref, curEvent));
      }
    }, 0);

    const dropdonwValue = DomUtil.get('ddlViewBy');
    // replace this with a default value
    console.log("basin: " + this.current_basin.properties.Major_Basin);
    
    // let alert_level_color = objref.mapUtil.color_lookup[];
    // console.log("alert level color: " + alert_level_color);
    // e.layer.setStyle({ color: alert_level_color, weight: 2 });



    console.log(`event properties target:  ${this.listProperties(e.target)}`);
    // getting the basin name... below
    console.log(`basin is: ${e.layer.feature.properties.Major_Basin}`);


    this.current_basin.style = { color: 'red', weight: 2 };
    //e.target.setStyle({ color: 'red', weight: 2 });



  }


  // popupevent(layer: any) {
  //   console.log("target attrib: " + layer.target);
  //   console.log("popup open event" + layer);
  //   console.log("event type: " + layer.type);
  //   // console.log(`mouse event properties: ${this._source}`);
  //   console.log(`obj properties:  ${this.listProperties(layer)}`);
  //   console.log(`obj properties popup:  ${this.listProperties(layer.popup, true)}`);
  //   console.log(`obj properties popup source:  ${layer.popup._source}`);

  //   console.log(`obj properties target  ${this.listProperties(layer.target)}`);
  //   console.log(`obj properties sourceTarget  ${this.listProperties(layer.sourceTarget)}`);
  //   console.log("event sourceTarget from: " + layer.originalEvent);
  //   console.log(`current basin: ${this.current_basin}`);
  //   console.log(`current basin properties: ${this.listProperties(this.current_basin)}`);


  //   console.log(layer);
  //   const popupContent = layer.popup.getContent();
  //   const saveButton = document.getElementById('saveAlertLevel');

  //   if (saveButton) {
  //     saveButton.addEventListener('click', () => this.setAlertLevel(layer));
  //     console.log("added save button event listener, button..." + saveButton + ' ' + typeof (layer));
  //   }
  // }

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

      this.current_basin.style = { color: 'red', weight: 2 };
      //e.target.setStyle({ color: 'red', weight: 2 });

      var myPopup = popup()
        .setLatLng(e.latlng)
        .setContent(this.mapUtil.dropdown);
      myPopup.openOn(map)
    });
  }

  styleMap = (feature: any): any => {
    console.log(`feature is: ${JSON.stringify(feature.properties.Major_Basin)}`);
    return { color: "blue", weight: 2 };
  }

  basin_lvl_lu_func = (basin_name: string): string => {
    return "None";
  }

  // public setAlertLevel(layer: any) {
  //   console.log("setting alert level...");
  //   const dropdonwValue = DomUtil.get('ddlViewBy');
  //   let alert_level = "None";
  //   if (dropdonwValue) {
  //     const selectElem = dropdonwValue as HTMLSelectElement;
  //     alert_level = selectElem.options[selectElem.selectedIndex].value;
  //   }
  //   console.log("basin: " + this.current_basin.properties.Major_Basin);
    //this.current_basin.style.color = 'red';
    // this.current_basin.style = { color: 'red', weight: 2 }
    //this.current_basin.setStyle({ color: 'red', weight: 2 });


    // layer.setStyle({
    //     weight: 5,
    //     color: '#666',
    //     dashArray: '',
    //     fillOpacity: 0.7
    // });

    // layer.bringToFront();




  //   console.log("alert level: " + alert_level);
  //   this._map.closePopup()
  //   // TODO: change color of underlying layer

  // }

  /*
    *  Function to list the properties of an object, helping to understand what 
    *  properties are available to be accessed, and what different leaflet events
    *  are returning.
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
