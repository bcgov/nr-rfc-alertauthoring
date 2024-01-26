import { RouterModule, Routes } from '@angular/router';
import { BasinListComponent } from './basin-list/basin-list.component';
import { AlertListComponent } from './alert-list/alert-list.component';
import { HomeComponent } from './home/home.component';
import { UnauthorizedComponent } from './unauthorized/unauthorized.component';
import {LoginComponent} from './login/login.component';

export const routes: Routes = [
    // { path: '', component: AlertListComponent },
    // { path: 'home', component: HomeComponent},
    { path: 'alertlist', component: AlertListComponent },
    { path: 'basins', component: BasinListComponent },
    { path: 'login', component: LoginComponent},
    { path: '', redirectTo: 'alertlist', pathMatch: 'full' },
];
