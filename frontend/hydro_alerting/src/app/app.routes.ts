import { RouterModule, Routes } from '@angular/router';
import { BasinListComponent } from './basin-list/basin-list.component';
import { AlertListComponent } from './alert-list/alert-list.component';
import { HomeComponent } from './home/home.component';
import { UnauthorizedComponent } from './unauthorized/unauthorized.component';
import {LoginComponent} from './login/login.component';
import {CreateAlertComponent} from './alerts/create-alert/create-alert.component';
import { EditAlertComponent } from './alerts/edit-alert/edit-alert.component';
import { ViewAlertComponent } from './alerts/view-alert/view-alert.component';

export const routes: Routes = [
    // { path: '', component: AlertListComponent },
    // { path: 'home', component: HomeComponent},
    { path: 'alertlist', component: AlertListComponent },
    { path: 'basins', component: BasinListComponent },
    { path: 'login', component: LoginComponent},
    { path: 'create_alert', component: CreateAlertComponent},
    { path: 'alert/:id/edit', component: EditAlertComponent },
    { path: 'alert/:id', component: ViewAlertComponent },
    { path: '', redirectTo: 'alertlist', pathMatch: 'full' },
];
