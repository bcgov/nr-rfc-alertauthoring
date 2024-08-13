import { tileLayer, Map, map, DomUtil, Control, popup } from 'leaflet';
import { featureLayer, FeatureLayer } from "esri-leaflet";


export class MapUtil {
    color_lookup: { [key: string]: string };
    default_zoom_level: number = 5;
    default_zoom_coords: [number, number] = [54.329, -125.837];


    constructor() {
        this.color_lookup = {
            "High Streamflow Advisory": "yellow",
            "Flood Watch": "orange",
            "Flood Warning": "red"
        }
    }

    getMapObj() : any {
        console.log("getting here...");
        console.log(`zoom level: ${this.default_zoom_level}`);
        let mapObj: Map = map('map').setView(this.default_zoom_coords, this.default_zoom_level);
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
    }
}


export const default_zoom_coords: [number, number] = [54.329, -125.837];
export const default_zoom_level = 5;

export const getMapObj = () : any => {
    console.log("getting here...");
    console.log(`zoom level: ${default_zoom_level}`);
    let mapObj: Map = map('map').setView(default_zoom_coords, default_zoom_level);
    let osMap = tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });
    osMap.addTo(mapObj);
    console.log("returning the map object")
    return mapObj;
}

export const addBasins = (map: Map, styleFunction: any) => {
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
