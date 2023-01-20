import { BrowserAnimationsModule } from '@angular/platform-browser/animations'; 
import { FlexLayoutModule } from '@angular/flex-layout';
import { NgModule } from '@angular/core';
import { FormsModule, ReactiveFormsModule } from '@angular/forms';
import { AppComponent } from './app.component';
import {AgmCoreModule} from "@agm/core";
import {CommonModule} from "@angular/common";
import {BrowserModule} from "@angular/platform-browser";
import {HttpClientModule} from "@angular/common/http";
import { MaterialModule } from './material.module';
import { NgChartsModule } from 'ng2-charts';
import { AlertComponent } from './components/alert/alert.component';
import { AlertsDialogComponent } from './components/alerts-dialog/alerts-dialog.component';

@NgModule({
  declarations: [
    AppComponent,
    AlertComponent,
    AlertsDialogComponent
  ],
  imports: [
    CommonModule,
    HttpClientModule,
    BrowserModule,
    AgmCoreModule.forRoot({
      apiKey: 'AIzaSyCSOdnwM7qZCxLt4G_uALn8_J4AGd9OCrQ'
    }),
    MaterialModule,
    FlexLayoutModule,
    NgChartsModule,
    BrowserAnimationsModule,
    FormsModule,
    ReactiveFormsModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
