import { Basin } from './basin';

export interface AlertLevel {
    alert_level: string;
    alert_level_id: number;
}

export interface AlertAreaLevels {
    basin: Basin;
    alert_level: AlertLevel;
}

// todo: tighten up the allowed values by adding domain constraints

export interface Alert {
    alert_id: number;
    alert_description: string;
    alert_hydro_conditions: string;
    alert_meteorological_conditions: string;
    alert_created: string;
    alert_updated: string;
    author_name: string;
    alert_status: string;
    alert_links?: [AlertAreaLevels] | undefined;
}