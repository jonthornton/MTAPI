import { Component, OnInit } from '@angular/core';
import {TrainById, TrainByRoute, TrainRoutes} from "../shared/actions/train.actions";
import {Store} from "@ngrx/store";
import {BehaviorSubject, Observable} from "rxjs";

@Component({
  selector: 'app-train',
  templateUrl: './train.component.html',
  styleUrls: ['./train.component.css']
})
export class TrainComponent implements OnInit {
  lat: number = 40.7831;
  lng: number = -73.9712;
  selectedRoute: boolean = false;
  chosenRoute: string = "";
  selectedStation: boolean = false;
  chosenStation: string = "";

  center: google.maps.LatLngLiteral = {lat: this.lat, lng: this.lng};

  // routes subscription
  routesSuccess$: Observable<any>;
  routesData: any[] = [];
  routesDataUpdated: any = "";

  routesFail$: Observable<any>;
  routesError: any = "";

  // given route, stations subscription
  stationsByRouteSuccess$: Observable<any>;
  routeStationsData: any[] = [];
  routeStationsDataUpdated: any = "";

  stationsByRouteFail$: Observable<any>;
  routeStationsError: any = "";

  // given station id, get station object
  stationsByIdSuccess$: Observable<any>;
  idStationData: any = [];
  idStationDataUpdated: any = "";

  stationsByIdFail$: Observable<any>;
  idStationError: any = "";

  markerOptions: google.maps.MarkerOptions = {draggable: false, icon: "/assets/images/subway-marker.png"};
  markerPositions: google.maps.LatLngLiteral[] = [];

  constructor(private store: Store<any>) {
    this.routesSuccess$ = this.store.select(s => s.trainRoutes.data);
    this.routesSuccess$.subscribe((data: any) => {
      if (data) {
        this.routesData = data.data;
        this.routesDataUpdated = data.updated;
        this.routesError = "";
      } else {
        this.routesData = [];
        this.routesDataUpdated = "";
      }
    })

    this.routesFail$ = this.store.select(s => s.trainRoutes.error);
    this.routesFail$.subscribe((error: any) => {
      if (error) {
        this.routesError = error;
        this.routesData = [];
        this.routesDataUpdated = "";
      } else {
        this.routesError = "";
      }
    })

    this.stationsByRouteSuccess$ = this.store.select(s => s.trainByRoute.data);
    this.stationsByRouteSuccess$.subscribe((data: any) => {
      if (data) {
        this.routeStationsData = data.data;
        let routeStationsDataCopy = [...this.routeStationsData];

        this.routeStationsData = routeStationsDataCopy.sort((first: any, second: any) => {
          if (first.location[0] < second.location[0]) {
            return -1;
          }
          if (first.location[0] > second.location[0]) {
            return 1;
          }
          return 0;
        });

        this.routeStationsDataUpdated = data.updated;
        this.routeStationsError = "";

        this.constructStationMarkers();
      } else {
        this.routeStationsData = [];
      }
    })

    this.stationsByRouteFail$ = this.store.select(s => s.trainByRoute.error);
    this.stationsByRouteFail$.subscribe((error: any) => {
      if (error) {
        this.routeStationsError = error;
        this.routeStationsData = [];
        this.routeStationsDataUpdated = "";
      } else {
        this.routeStationsError = "";
      }
    })

    this.stationsByIdSuccess$ = this.store.select(s => s.trainById.data);
    this.stationsByIdSuccess$.subscribe((data: any) => {
      if (data) {
        this.idStationData = data.data;
        this.idStationDataUpdated = data.updated;
        this.idStationError = "";
      } else {
        this.idStationDataUpdated = [];
        this.idStationDataUpdated = "";
      }
    })

    this.stationsByIdFail$ = this.store.select(s => s.trainById.error);
    this.stationsByIdFail$.subscribe((error: any) => {
      if (error) {
        this.idStationError = error;
        this.idStationData = [];
        this.idStationDataUpdated = "";
      } else {
        this.idStationError = "";
      }
    })

    this.store.dispatch(TrainRoutes());
  }

  ngOnInit(): void {
  }

  reload(): void {
    this.store.dispatch(TrainById({request: {ids: [this.chosenStation]}}));
  }

  selectRoute(event: any) {
    this.selectedRoute = true;
    this.chosenRoute = event.source.value;
    this.store.dispatch(TrainByRoute({request: {route: event.source.value}}));
    this.idStationData = [];
    this.markerPositions = [];
  }

  selectStation(event: any) {
    this.selectedStation = true;
    this.idStationData = [];
    this.chosenStation = event.source.value.id;
    this.store.dispatch(TrainById({request: {ids: [event.source.value.id]}}));
    this.lat = event.source.value.location[0];
    this.lng = event.source.value.location[1];
    this.center = {lat: this.lat, lng: this.lng};
  }

  constructStationMarkers() {
    for (let station of this.routeStationsData) {
      this.markerPositions.push({lat: station.location[0], lng: station.location[1]});
    }
  }
}
