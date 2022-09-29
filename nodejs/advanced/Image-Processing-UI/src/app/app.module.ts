import { NgModule } from '@angular/core';
import { AppComponent } from './app.component';
import {AgmCoreModule} from "@agm/core";
import {CommonModule} from "@angular/common";
import {BrowserModule} from "@angular/platform-browser";
import {HttpClientModule} from "@angular/common/http";

@NgModule({
  declarations: [
    AppComponent,
  ],
  imports: [
    CommonModule,
    HttpClientModule,
    BrowserModule,
    AgmCoreModule.forRoot({
      apiKey: 'AIzaSyCSOdnwM7qZCxLt4G_uALn8_J4AGd9OCrQ'
    })
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
