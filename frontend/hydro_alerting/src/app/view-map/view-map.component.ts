import { Component, OnInit, AfterViewInit, ViewChild, ElementRef, Input } from '@angular/core';
import { Map, map, tileLayer, popup, Control, DomUtil } from 'leaflet';
import { featureLayer } from "esri-leaflet";
import { AlertAreaLevels } from '../types/alert';


@Component({
  selector: 'app-view-map',
  standalone: true,
  imports: [],
  templateUrl: './view-map.component.html',
  styleUrl: './view-map.component.css'
})
export class ViewMapComponent implements OnInit, AfterViewInit {
  @Input() alertLevel?: AlertAreaLevels[];
  @ViewChild('map')

  alert_levels: any = {};
  alert_levels_list: string[] = [];
  basins: string[] = [];
  basinStyles: any = {};

  color_lookup: { [key: string]: string } = {
    "High Streamflow Advisory": "yellow",
    "Flood Watch": "orange",
    "Flood Warning": "red"
  }

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
        this.basinStyles[this.alertLevel[i].basin.basin_name] = this.color_lookup[this.alertLevel[i].alert_level.alert_level];
      }
    }


  }

  ngAfterViewInit() {

    this.initializeMap();
  }

  private styleMap(feature: any) {
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

  private initializeMap() {
    let alert_levels = this.alert_levels
    console.log("alert levels are: " + JSON.stringify(this.alert_levels));

    this._map = map('map').setView([54.329, -125.837], 5);
    let mapref = this._map;
    var osMap = tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    });
    osMap.addTo(this._map);

    // add legend
    let legend = this.defineLegend(this._map);
    legend.addTo(this._map);


    // let earthquakes = "https://sampleserver6.arcgisonline.com/arcgis/rest/services/Earthquakes_Since1970/MapServer/0";
    let basins_url = "https://services6.arcgis.com/ubm4tcTYICKBpist/arcgis/rest/services/BC_Flood_Advisory_and_Warning_Notifications_(Public_View)/FeatureServer/0"
    let basins_fl = featureLayer({
      url: basins_url,
      where: "Basin_Type = 'N'",
      simplifyFactor: .75,
      precision: 2,
      style: this.styleMap.bind(this)
    });


    basins_fl.on('click', (e: any): any => {
      console.log(e.layer.feature.properties);
      // let lvl = getAlertLevel(e.layer.feature.properties.Major_Basin);
      let lvl = 'high';
      console.log("basins: " + this.basins);
      console.log(`alert levels: ${this.alert_levels_list}`);

      let alert_level = this.alert_levels_list[this.basins.indexOf(e.layer.feature.properties.Major_Basin)];
      if (!alert_level) {
        alert_level = "None";
      }
      alert_level = 'Alert Level: <b>' + alert_level + '</b>'

      var myPopup = popup()
        .setLatLng(e.latlng)
        .setContent(`<p>Basin: <b>${e.layer.feature.properties.Major_Basin}</b><br>${alert_level}</p>`);
      // .bindPopup(`<p>${e.layer.feature.properties.Major_Basin}!<br>${lvl}<br>${alert_levels}</p>`);
      // .setContent(`<p>${e.layer.feature.properties.Major_Basin}!<br>${lvl}<br>${alert_levels}</p>`);
      myPopup.openOn(mapref);
    });
    basins_fl.addTo(this._map);

    // this._map.invalidateSize();

    // flood advisories
    // https://services6.arcgis.com/ubm4tcTYICKBpist/arcgis/rest/services/BC_Flood_Advisory_and_Warning_Notifications_(Public_View)/FeatureServer/0
  }

  private defineLegend(map: Map) {
    var legend = new Control({ position: 'bottomright' });
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
          // '<div id="legendcircle"><svg x="0" y="0" width="10" height="10" fill="blue"></svg><span>text text</span></div>'
          // <svg viewBox="0 0 220 100" xmlns="http://www.w3.org/2000/svg">
          // <div id="rectangle" style="width:number px; height:number px; background-color:blue"></div>
          //             '<i class="legendcircle" style="background:' + this.color_lookup[alert_level_string] + '; width:10px; height:10px"></i> ' +
            // '<span>' + alert_level_string + '</span>');
            // <rect x="120" width="100" height="100" rx="15" />

        console.log(`div: ${div.innerHTML}`);
        console.log(`labels: ${labels}`);
      }
      div.innerHTML = labels.join('<br>');
      return div;
    };
    return legend;
  }

}
