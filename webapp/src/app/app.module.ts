import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';

import { AppComponent } from './app.component';
import { TrainComponent } from './train/train.component';
import { BusComponent } from './bus/bus.component';
import { AsyncTrainService} from "./shared/services/async-train.service";
import {AsyncBusService} from "./shared/services/async-bus.service";
import {HttpClientModule} from "@angular/common/http";
import {reducers} from "./shared/reducers";
import { StoreModule } from '@ngrx/store';
import { EffectsModule } from '@ngrx/effects';
import {TrainEffects} from "./shared/effects/train.effects";
import {BusEffects} from "./shared/effects/bus.effects";
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import {MatTabsModule} from "@angular/material/tabs";
import {MatToolbarModule} from "@angular/material/toolbar";
import {MatIconModule} from "@angular/material/icon";
import {GoogleMapsModule} from "@angular/google-maps";
import {MatFormFieldModule} from "@angular/material/form-field";
import {MatSelectModule} from "@angular/material/select";
import {MatOptionModule} from "@angular/material/core";
import {FormsModule} from "@angular/forms";

@NgModule({
  declarations: [
    AppComponent,
    TrainComponent,
    BusComponent,
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    StoreModule.forRoot(reducers),
    EffectsModule.forRoot([TrainEffects, BusEffects]),
    BrowserAnimationsModule,
    MatTabsModule,
    MatToolbarModule,
    MatIconModule,
    GoogleMapsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatOptionModule,
    FormsModule
  ],
  providers: [AsyncBusService, AsyncTrainService],
  bootstrap: [AppComponent]
})
export class AppModule { }
