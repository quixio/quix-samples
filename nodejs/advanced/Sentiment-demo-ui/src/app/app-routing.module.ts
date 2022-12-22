import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import {WebchatComponent} from "./components/webchat/webchat.component";
import {LobbyComponent} from "./components/lobby/lobby.component";


const routes: Routes = [
  {path: '', redirectTo: '/lobby', pathMatch: 'full'},
  {path: 'webchat/:room/:name', component: WebchatComponent},
  {path: 'lobby', component: LobbyComponent},
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule { }