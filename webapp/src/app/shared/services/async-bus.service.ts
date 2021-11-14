import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders, HttpParams } from "@angular/common/http";
import {Observable} from "rxjs";
import {map, catchError} from "rxjs/operators";

//let BusRestAPIUrl = 'http://' + self.location.host.split(':')[0] +':5000/bus'
let BusRestAPIUrl = 'http://127.0.0.1:5000/bus';

@Injectable({
  providedIn: 'root'
})
export class AsyncBusService {

  constructor(private http: HttpClient) { }

  byLocation(latitude: number, longitude: number, num: number): Observable<any> {
    let apiUrl = BusRestAPIUrl + "/by-location";
    let headers = new HttpHeaders();
    let params = new HttpParams();

    params.set("lat", latitude);
    params.set("lon", longitude);
    params.set("num", num);

    return this.executeRequest(apiUrl, headers, params);
  }

  byRoute(route: string): Observable<any> {
    let apiUrl = BusRestAPIUrl + "/by-route/" + route;
    let headers = new HttpHeaders();
    let params = new HttpParams();

    return this.executeRequest(apiUrl, headers, params);
  }

  byId(ids: any[]): Observable<any> {
    let apiUrl = BusRestAPIUrl + "/by-id/"
    let headers = new HttpHeaders();
    let params = new HttpParams();

    // construct the correct url for by-id
    for (let i = 0; i < ids.length; i++) {
      if (i == ids.length - 1) {
        apiUrl += ids[i];
      } else {
        apiUrl += ids[i] + ",";
      }
    }

    return this.executeRequest(apiUrl, headers, params);
  }

  routes(): Observable<any> {
    let apiUrl = BusRestAPIUrl + "/routes";
    let headers = new HttpHeaders();
    let params = new HttpParams();

    return this.executeRequest(apiUrl, headers, params);
  }

  executeRequest(apiUrl: string, headers: any, params: any): Observable<any> {
    return this.http.post<any>(apiUrl, {}, ({headers: headers, params: params}))
      .pipe(map((response: Response) => { return response; }),
        catchError((error: any) => this.handleError(error)))
  }

  private handleError(error: any): Promise<any> {
    console.log("request error")
    console.log(error)
    return Promise.reject(error.error || error)
  }
}