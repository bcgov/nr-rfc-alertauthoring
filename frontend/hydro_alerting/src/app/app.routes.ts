import { RouterModule, Routes } from '@angular/router';
import { BasinListComponent } from './basin-list/basin-list.component';
import { AlertListComponent } from './alerts/alert-list/alert-list.component';
import {CreateAlertComponent} from './alerts/create-alert/create-alert.component';
import { EditAlertComponent } from './alerts/edit-alert/edit-alert.component';
import { ViewAlertComponent } from './alerts/view-alert/view-alert.component';
import { UnauthorizedComponent } from './unauthorized/unauthorized.component';
import {AuthorizationGuard} from './guards/editor.guard';

export const routes: Routes = [
    // { path: '', component: AlertListComponent },
    // { path: 'home', component: HomeComponent},
    { path: 'alert/list', component: AlertListComponent },
    { path: 'basins', component: BasinListComponent },
    { path: 'alert/create', component: CreateAlertComponent, canActivate: [AuthorizationGuard]},
    { path: 'alert/:id/edit', component: EditAlertComponent, canActivate: [AuthorizationGuard] },
    { path: 'alert/:id', component: ViewAlertComponent },
    { path: 'unauthorized', component: UnauthorizedComponent},
    { path: '', redirectTo: 'alert/list', pathMatch: 'full' },
];
