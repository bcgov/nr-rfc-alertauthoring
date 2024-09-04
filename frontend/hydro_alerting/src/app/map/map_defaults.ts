import { tileLayer, Map, map, DomUtil, Control, popup } from 'leaflet';
import { featureLayer, FeatureLayer } from "esri-leaflet";


export class MapUtil {
  color_lookup: { [key: string]: string };
  default_zoom_level: number = 5;
  default_zoom_coords: [number, number] = [54.329, -125.837];

  dropdown!: string;

  constructor() {
    // This should originate from the service... 
    // either pass the data in from the parent compoent via an input, 
    // or get the data directly from the service
    this.color_lookup = {
      "High Streamflow Advisory": "yellow",
      "Flood Watch": "orange",
      "Flood Warning": "red"
    }
  }

  /**
   * injects basin name into html to create the content to be displayed in the popup
   * 
   * @param basin - the input basin name
   * @returns html content to be inserted into a leaflet popup
   */
  public getPopupContent(basin: string): string {
    let popupContent = `Set the Alert Level for the Basin: <b>${basin}</b> ` +
      `<select id="ddlViewBy">; `;
    for (const alert_level_string in this.color_lookup) {
      console.log("alert level string is: " + alert_level_string + ' ' + this.color_lookup[alert_level_string]);
      popupContent += `<option value="${alert_level_string}">${alert_level_string}</option>`;
    }
    popupContent += '</select>: <button id="saveAlertLevel">save</button>';
    return popupContent
  }

  /**
   * This is the method that gets called when the save button on the popup selecting
   * the alert level for a basin is clicked on.
   * 
   * @param e pointer event from clicking on the save button inside the popup
   * @param basin the basin that the alert level is being set for
   * @param objref reference to the create-map component
   * @param curEvent the popup leaflet event associated with the popup who's save
   *               button was clicked on, sending us here
   */
  public setAlertLevel(e: any, basin: string, objref: any, curEvent: any) {

    // getting the popup html element
    const dropDownValue = DomUtil.get('ddlViewBy');
    let alert_level = "None"; // default alert level value
    if (dropDownValue) {
      // if there is a popup  open, then get the alert level associated with it
      const selectElem = dropDownValue as HTMLSelectElement;
      alert_level = selectElem.options[selectElem.selectedIndex].value;

      // now that we have the alert level, close the  popup
      objref._map.closePopup();

      // this needs to be refactored to use a data struct that a style method 
      // will call, doing things this way will only result in a temporary 
      // change of colors for the polygon
      let alert_level_color = objref.mapUtil.color_lookup[alert_level];
      console.log("alert level color: " + alert_level_color);
      objref.styleMap(curEvent.layer.feature, objref.basinLvlDataService, this.color_lookup, objref)

      console.log("feature id: " + curEvent.layer.feature.id);
      console.log("number of features: " + curEvent.layer.length);
      curEvent.layer.setStyle({ color: alert_level_color, weight: 2 });

      // ^ this should just pass the alert level and basin to the original
      //   setStyle method.... which is going to read the objref.basinLvlDataService
      //   and style the polygon

      // propogate the basin / alert level to a new basin / alert level component
      let comp_id = objref.basinLvlDataService.getEmptyComponentId();
      objref.basinLvlDataService.addBasin(basin, comp_id);
      objref.basinLvlDataService.addAlertLvl(alert_level, comp_id);
    }
  }

  /**
   * The method will do the following to the map:
   * - add a basemap
   * - set the zoom level to zoom in on the province of BC
   * 
   * @param mapObj - the leaflet map object that will be configured by this method.
   * @returns a leaflet map object that has been configured
   */
  public getMapObj(mapObj: Map): any {
    mapObj = map('map').setView(this.default_zoom_coords, this.default_zoom_level);
    mapObj.invalidateSize();
    let osMap = tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });
    osMap.addTo(mapObj);
    console.log("returning the map object")
    return mapObj;
  }

  /**
   * 
   * @returns a leaflet control object that will be used to display the legend
   */
  public defineLegend(): Control {
    let legend = new Control({ position: 'bottomright' });
    legend.onAdd = (map) => {
      var div = DomUtil.create('div', 'legend');
      let labels = ['<strong>Categories</strong>'];
      for (const alert_level_string in this.color_lookup) {
        console.log("alert level string is: " + alert_level_string + ' ' + this.color_lookup[alert_level_string]);
        div.innerHTML +=
          labels.push('<svg  x=0 y=0 width="10" height="10"> ' +
            '<rect width="100" height="100" fill="' + this.color_lookup[alert_level_string] + '"/> ' +
            '<span> ' + alert_level_string + '</span> ' +
            '</svg>')
      }
      div.innerHTML = labels.join('<br>');
      return div;
    };
    return legend;
  }

  /**
   * This method is intended for read only maps where the style of the polygons
   * is not dynamic.  See 'addBasinsEditCreate' if styles need to be dynamic.
   * 
   * The style function only needs to support recieving a basin feature, which
   * will look up if the basin has a specific style, and if so return that style.
   * otherwise returns a default style
   * 
   * @param styleFunction 
   * @returns 
   */
  public addBasins(styleFunction: any): FeatureLayer {
    let basins_url = "https://services6.arcgis.com/ubm4tcTYICKBpist/arcgis/rest/services/BC_Flood_Advisory_and_Warning_Notifications_(Public_View)/FeatureServer/0"
    let basins_fl = featureLayer({
      url: basins_url,
      where: "Basin_Type = 'N'",
      simplifyFactor: .75,
      precision: 2,
      style: (feature) => { styleFunction(feature) }
    });
    console.log("adding basins to map");
    return basins_fl;
  }

  /**
   * adds a feature layer to the map that will allow the user to edit the alert
   * either via the map, or via the alert level selector component.
   * 
   * @param styleFunction - the callback style function.  It will recieve a feature
   *                      object, and should return a style object.
   * @param basinLvlService - the service that keeps track of the state of the basin 
   *                       alert levels, updates to this service will update the map component
   *                      and the alert level of the basin non spatial selector component.    
   *                         
   * @param objRef - a reference to the createMap component. Seeing as its used as 
   *                 a callback it loses track of the 'this' context, so this is a
   *                reference to the createMap component.
   * @returns 
   */
  public addBasinsEditCreate(styleFunction: any, basinLvlService: any, objRef: any): FeatureLayer {
    let basins_url = "https://services6.arcgis.com/ubm4tcTYICKBpist/arcgis/rest/services/BC_Flood_Advisory_and_Warning_Notifications_(Public_View)/FeatureServer/0"
    let basins_fl = featureLayer({
      url: basins_url,
      where: "Basin_Type = 'N'",
      simplifyFactor: .75,
      precision: 2,
      style: (feature) => { objRef.styleMap(feature, objRef.basinLvlService, this.color_lookup, objRef) }
    });
    return basins_fl;
  }

  /**
   * used for read only maps... popup will show the basin and alert level that
   * have already been set
   * 
   * @param map  - leaflet map object
   * @param basins_fl - the esri leaflet basin feature layer
   * @param basin_level_func - function that will return the alert level for a basin
   */
  addBasinPopup(map: Map, basins_fl: FeatureLayer, basin_level_func: CallableFunction): void {
    basins_fl.on('click', (e: any): any => {
      // let alert_level = this.alert_levels_list[this.basins.indexOf(e.layer.feature.properties.Major_Basin)];
      let alert_level = basin_level_func(e.layer.feature.properties.Major_Basin);
      if (!alert_level) {
        alert_level = "None";
      }
      alert_level = 'Alert Level: <b>' + alert_level + '</b>'

      var myPopup = popup()
        .setLatLng(e.latlng)
        .setContent(`<p>Basin: <b>${e.layer.feature.properties.Major_Basin}</b><br>${alert_level}</p>`);
      myPopup.openOn(map);
    });
  }

  /**
   * used for write / edit forms where the basin / alert-levels can be set either
   * via the map or via the alert level selector component
   * 
   * @param map - reference to the leaflet map component
   * @param basins_fl - reference to the esri leaflet feature layer for basins
   * @param basin_level_func - the lookup function that given a basin name will return
   *                        the alert level.
   */
  addBasinAlertLevelSetterPopup(map: Map, basins_fl: FeatureLayer, basin_level_func: CallableFunction): void {
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
        .setContent(this.dropdown);
      // .setContent(`<p>Basin: <b>${e.layer.feature.properties.Major_Basin}</b><br>${alert_level}</p>`);
      myPopup.openOn(map);
    });
  }
}


