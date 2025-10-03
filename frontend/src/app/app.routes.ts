import {NgModule} from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {Dashboard} from './dashboard/dashboard';
import {Drivers} from './drivers/drivers';
import {Teams} from './teams/teams';
import {Races} from './races/races';

export const routes: Routes = [
  {path: 'dashboard', component: Dashboard},
  {path: 'drivers', component: Drivers},
  {path: 'teams', component: Teams},
  {path: 'races', component: Races},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {}

