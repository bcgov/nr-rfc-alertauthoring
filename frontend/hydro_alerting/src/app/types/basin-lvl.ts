import { Type } from '@angular/core';
import { BasinAlertlvlComponent } from '../basin-alerts/basin-alertlvl/basin-alertlvl.component';
import { Basin } from './basin';
export interface BasinLvl {
    basin_name: string;
    alert_level_name: string;
    event_type: string;
}

export interface BasinLvlDynamicComponent {
    // type for dynamic basin / alert level component
    component: Type<any>;
    inputs: {
        basin_name: string;
        alert_level_name: string;
        component_id: number;
    }
}

export interface newAlert{

}

