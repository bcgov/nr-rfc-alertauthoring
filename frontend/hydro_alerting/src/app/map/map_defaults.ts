import { tileLayer, Map, map, DomUtil, Control, popup } from 'leaflet';
import { featureLayer, FeatureLayer } from "esri-leaflet";


export class MapUtil {
    color_lookup: { [key: string]: string };
    default_zoom_level: number = 5;
    default_zoom_coords: [number, number] = [54.329, -125.837];

    dropdown! : string;

    constructor() {
      // This should originate from the service... 
      // either pass the data in from the parent compoent via an input, 
      // or get the data directly from the service
        this.color_lookup = {
            "High Streamflow Advisory": "yellow",
            "Flood Watch": "orange",
            "Flood Warning": "red"
        }
        this.dropdown = `Set the Alert Level for the Basin:
           <select id="ddlViewBy">; `;
        for (const alert_level_string in this.color_lookup) {
            console.log("alert level string is: " + alert_level_string + ' ' + this.color_lookup[alert_level_string]);
            this.dropdown += `<option value="${alert_level_string}">${alert_level_string}</option>`;
        }
        this.dropdown += '</select>: <button id="saveAlertLevel">save</button>';
        setTimeout(() => {
          const saveButton = document.getElementById('saveAlertLevel');
          console.log("added save button event listener, button..." + saveButton);
          if (saveButton) {
              saveButton.addEventListener('click', () => this.setAlertLevel());
          }
      }, 0);
  
    }
    
    public setAlertLevel() {
        console.log("setting alert level...");
        // const dropdonwValue = DomUtil.get('ddlViewBy');
        // console.log("dropdown value is: " + dropdonwValue);
      //   map.closePopup()
      //   L.marker(latLng)
      //     .bindPopup(dropdonwValue)
      //     .addTo(map)
      // }
    
    }


    getMapObj(mapObj: Map) : any {
        console.log("getting here...");
        console.log(`zoom level: ${this.default_zoom_level}`);
        console.log("map object is: " + mapObj);

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

    defineLegend(map: Map): Control {
        let legend = new Control({ position: 'bottomright' });
        legend.onAdd = (map) => {
          var div = DomUtil.create('div', 'legend');
          let labels = ['<strong>Categories</strong>'];
          for (const alert_level_string in this.color_lookup) {
            console.log("alert level string is: " + alert_level_string + ' ' + this.color_lookup[alert_level_string]);
            div.innerHTML +=
              labels.push('<svg  x=0 y=0 width="10" height="10"> ' + 
                '<rect width="100" height="100" fill="' + this.color_lookup[alert_level_string] + '"/> ' + 
                '<span> '+ alert_level_string+'</span> ' +
              '</svg>')
          }
          div.innerHTML = labels.join('<br>');
          return div;
        };
        return legend;
    }

    addBasins(map: Map, styleFunction: any): FeatureLayer {
        let basins_url = "https://services6.arcgis.com/ubm4tcTYICKBpist/arcgis/rest/services/BC_Flood_Advisory_and_Warning_Notifications_(Public_View)/FeatureServer/0"
        let basins_fl = featureLayer({
          url: basins_url,
          where: "Basin_Type = 'N'",
          simplifyFactor: .75,
          precision: 2,
          style: styleFunction
        });
        return basins_fl;
    }

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
          // myPopup.
    }
    

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


