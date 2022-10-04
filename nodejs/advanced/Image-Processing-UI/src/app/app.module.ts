import { NgModule } from '@angular/core';
import { AppComponent } from './app.component';
import {AgmCoreModule} from "@agm/core";
import {CommonModule} from "@angular/common";
import {BrowserModule} from "@angular/platform-browser";
import {HttpClientModule} from "@angular/common/http";
import {AppRoutingModule} from "./app-routing.module";
import {FormsModule} from "@angular/forms";

@NgModule({
  declarations: [
    AppComponent,
  ],
    imports: [
        CommonModule,
        HttpClientModule,
        AppRoutingModule,
        BrowserModule,
        AgmCoreModule.forRoot(),
        FormsModule
    ],
  providers: [
  ],
  bootstrap: [AppComponent]
})
export class AppModule { }
