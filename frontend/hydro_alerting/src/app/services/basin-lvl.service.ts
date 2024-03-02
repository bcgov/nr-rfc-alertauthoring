import { Injectable, Type } from '@angular/core';
import { BasinAlertlvlComponent } from '../basin-alertlvl/basin-alertlvl.component';

@Injectable({ providedIn: 'root' })
export class BasinLvlService {
  getBasinLevels() {
    // by default including a blank record
    return [
      {
        component: BasinAlertlvlComponent,
        // inputs: { basin_name: 'Skagit', alert_level: 'high' }, -- shows how to set default values, will be required when reading data from the backend for edit
        inputs: { basin_name: '', alert_level: '' },

      },
    ] as {component: Type<any>, inputs: Record<string, any>}[];
  }
}

