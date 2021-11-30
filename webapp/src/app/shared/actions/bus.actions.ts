import {Action, createAction, props} from "@ngrx/store";

export const BUS_BY_LOCATION =            '[LOCATION] By Location Bus';
export const BUS_BY_LOCATION_SUCCESS =    '[LOCATION] By Location Bus Success';
export const BUS_BY_LOCATION_FAIL =       '[LOCATION] By Location Bus Fail';

export const BUS_BY_ROUTE =               '[ROUTE] By Route Bus';
export const BUS_BY_ROUTE_SUCCESS =       '[ROUTE] By Route Bus Success';
export const BUS_BY_ROUTE_FAIL =          '[ROUTE] By Route Bus Fail';

export const BUS_BY_IDS =                 '[IDS] By Ids Bus';
export const BUS_BY_IDS_SUCCESS =         '[IDS] By Ids Bus Success';
export const BUS_BY_IDS_FAIL =            '[IDS] By Ids Bus Fail';

export const BUS_ROUTES =                 '[ROUTES] Routes Bus';
export const BUS_ROUTES_SUCCESS =         '[ROUTES] Routes Bus Success';
export const BUS_ROUTES_FAIL =            '[ROUTES] Routes Bus Fail';

export const BUS_ALL_ALERTS_BY_ROUTE =    '[ALLALERTS] All Alerts By Route Bus';
export const BUS_ALL_ALERTS_BY_ROUTE_SUCCESS = '[ALLALERTS] All Alerts By Route Bus Success';
export const BUS_ALL_ALERTS_BY_ROUTE_FAIL = '[ALLALERTS] All Alerts By Route Bus Fail';

export const BUS_ALERT_BY_ROUTE = '[ALERTBYROUTE] Alert By Route Bus';
export const BUS_ALERT_BY_ROUTE_SUCCESS = '[ALERTBYROUTE] Alert By Route Bus Success';
export const BUS_ALERT_BY_ROUTE_FAIL = '[ALERTBYROUTE] Alert By Route Bus Fail';

export const BUS_ALERT_BY_STOP = '[ALERTBYSTOP] Alert By Stop Bus';
export const BUS_ALERT_BY_STOP_SUCCESS = '[ALERTBYSTOP] Alert By Stop Bus Success';
export const BUS_ALERT_BY_STOP_FAIL = '[ALERTBYSTOP] Alert By Stop Bus Fail';

export interface BusByLocationRequest {
    lat: number,
    lon: number,
    num: number
}

export interface BusByRouteRequest {
    route: string
}

export interface BusByIdRequest {
    ids: any[]
}

export interface BusAllAlertsByRouteRequest {
    route: string
}

export interface BusAlertsByStopRequest {
    stop: string;
}

// by-location Actions
export const BusByLocation = createAction(
    BUS_BY_LOCATION,
    props<{
        request: BusByLocationRequest
    }>()
)

export const BusByLocationSuccess = createAction(
    BUS_BY_LOCATION_SUCCESS,
    props<{
        data: any
    }>()
)

export const BusByLocationFail = createAction(
    BUS_BY_LOCATION_FAIL,
    props<{
        error: any
    }>()
)

// by-route Actions
export const BusByRoute = createAction(
    BUS_BY_ROUTE,
    props<{
        request: BusByRouteRequest
    }>()
)

export const BusByRouteSuccess = createAction(
    BUS_BY_ROUTE_SUCCESS,
    props<{
        data: any
    }>()
)

export const BusByRouteFail = createAction(
    BUS_BY_ROUTE_FAIL,
    props<{
        error: any
    }>()
)

// by-ids Actions
export const BusById = createAction(
    BUS_BY_IDS,
    props<{
        request: BusByIdRequest
    }>()
)

export const BusByIdSuccess = createAction(
    BUS_BY_IDS_SUCCESS,
    props<{
        data: any
    }>()
)

export const BusByIdFail = createAction(
    BUS_BY_IDS_FAIL,
    props<{
        error: any
    }>()
)

// routes Actions
export const BusRoutes = createAction(
    BUS_ROUTES
)

export const BusRoutesSuccess = createAction(
    BUS_ROUTES_SUCCESS,
    props<{
        data: any
    }>()
)

export const BusRoutesFail = createAction(
    BUS_ROUTES_FAIL,
    props<{
        error: any
    }>()
)

// all alerts by route
export const BusAllAlertsByRoute = createAction(
    BUS_ALL_ALERTS_BY_ROUTE,
    props<{
        request: BusAllAlertsByRouteRequest
    }>()
)

export const BusAllAlertsByRouteSuccess = createAction(
    BUS_ALL_ALERTS_BY_ROUTE_SUCCESS,
    props<{
        data: any
    }>()
)

export const BusAllAlertsByRouteFail = createAction(
    BUS_ALL_ALERTS_BY_ROUTE_FAIL,
    props<{
        error: any
    }>()
)

// alert by route
// uses BusAllAlertsByRouteRequest interface because both just require route as the request
export const BusAlertByRoute = createAction(
    BUS_ALERT_BY_ROUTE,
    props<{
        request: BusAllAlertsByRouteRequest
    }>()
)

export const BusAlertByRouteSuccess = createAction(
    BUS_ALERT_BY_ROUTE_SUCCESS,
    props<{
        data: any
    }>()
)

export const BusAlertByRouteFail = createAction(
    BUS_ALERT_BY_ROUTE_FAIL,
    props<{
        error: any
    }>()
)

// alert by stop
export const BusAlertByStop = createAction(
    BUS_ALERT_BY_STOP,
    props<{
        request: BusAlertsByStopRequest
    }>()
)

export const BusAlertByStopSuccess = createAction(
    BUS_ALERT_BY_STOP_SUCCESS,
    props<{
        data: any
    }>()
)

export const BusAlertByStopFail = createAction(
    BUS_ALERT_BY_STOP_FAIL,
    props<{
        error: any
    }>()
)