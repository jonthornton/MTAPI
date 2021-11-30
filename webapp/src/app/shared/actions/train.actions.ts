import {Action, createAction, props} from "@ngrx/store";

export const TRAIN_BY_LOCATION =            '[LOCATION] By Location Train';
export const TRAIN_BY_LOCATION_SUCCESS =    '[LOCATION] By Location Train Success';
export const TRAIN_BY_LOCATION_FAIL =       '[LOCATION] By Location Train Fail';

export const TRAIN_BY_ROUTE =               '[ROUTE] By Route Train';
export const TRAIN_BY_ROUTE_SUCCESS =       '[ROUTE] By Route Train Success';
export const TRAIN_BY_ROUTE_FAIL =          '[ROUTE] By Route Train Fail';

export const TRAIN_BY_IDS =                 '[IDS] By Ids Train';
export const TRAIN_BY_IDS_SUCCESS =         '[IDS] By Ids Train Success';
export const TRAIN_BY_IDS_FAIL =            '[IDS] By Ids Train Fail';

export const TRAIN_ROUTES =                 '[ROUTES] Routes Train';
export const TRAIN_ROUTES_SUCCESS =         '[ROUTES] Routes Train Success';
export const TRAIN_ROUTES_FAIL =            '[ROUTES] Routes Train Fail';

export const TRAIN_ALL_ALERTS_BY_ROUTE =    '[ALLALERTS] All Alerts By Route Train';
export const TRAIN_ALL_ALERTS_BY_ROUTE_SUCCESS = '[ALLALERTS] All Alerts By Route Train Success';
export const TRAIN_ALL_ALERTS_BY_ROUTE_FAIL = '[ALLALERTS] All Alerts By Route Train Fail';

export const TRAIN_ALERT_BY_ROUTE = '[ALERTBYROUTE] Alert By Route Train';
export const TRAIN_ALERT_BY_ROUTE_SUCCESS = '[ALERTBYROUTE] Alert By Route Train Success';
export const TRAIN_ALERT_BY_ROUTE_FAIL = '[ALERTBYROUTE] Alert By Route Train Fail';

export const TRAIN_ALERT_BY_STOP = '[ALERTBYSTOP] Alert By Stop Train';
export const TRAIN_ALERT_BY_STOP_SUCCESS = '[ALERTBYSTOP] Alert By Stop Train Success';
export const TRAIN_ALERT_BY_STOP_FAIL = '[ALERTBYSTOP] Alert By Stop Train Fail';

export interface TrainByLocationRequest {
  lat: number,
  lon: number,
  num: number
}

export interface TrainByRouteRequest {
  route: string
}

export interface TrainByIdRequest {
  ids: any[]
}

export interface TrainAllAlertsByRouteRequest {
  route: string
}

export interface TrainAlertsByStopRequest {
    stop: string;
}

// by-location Actions
export const TrainByLocation = createAction(
  TRAIN_BY_LOCATION,
  props<{
    request: TrainByLocationRequest
  }>()
)

export const TrainByLocationSuccess = createAction(
  TRAIN_BY_LOCATION_SUCCESS,
  props<{
    data: any
  }>()
)

export const TrainByLocationFail = createAction(
  TRAIN_BY_LOCATION_FAIL,
  props<{
    error: any
  }>()
)

// by-route Actions
export const TrainByRoute = createAction(
  TRAIN_BY_ROUTE,
  props<{
    request: TrainByRouteRequest
  }>()
)

export const TrainByRouteSuccess = createAction(
  TRAIN_BY_ROUTE_SUCCESS,
  props<{
    data: any
  }>()
)

export const TrainByRouteFail = createAction(
  TRAIN_BY_ROUTE_FAIL,
  props<{
    error: any
  }>()
)

// by-ids Actions
export const TrainById = createAction(
  TRAIN_BY_IDS,
  props<{
    request: TrainByIdRequest
  }>()
)

export const TrainByIdSuccess = createAction(
  TRAIN_BY_IDS_SUCCESS,
  props<{
    data: any
  }>()
)

export const TrainByIdFail = createAction(
  TRAIN_BY_IDS_FAIL,
  props<{
    error: any
  }>()
)

// routes Actions
export const TrainRoutes = createAction(
  TRAIN_ROUTES
)

export const TrainRoutesSuccess = createAction(
  TRAIN_ROUTES_SUCCESS,
  props<{
    data: any
  }>()
)

export const TrainRoutesFail = createAction(
  TRAIN_ROUTES_FAIL,
  props<{
    error: any
  }>()
)

// all alerts by route
export const TrainAllAlertsByRoute = createAction(
    TRAIN_ALL_ALERTS_BY_ROUTE,
    props<{
      request: TrainAllAlertsByRouteRequest
    }>()
)

export const TrainAllAlertsByRouteSuccess = createAction(
    TRAIN_ALL_ALERTS_BY_ROUTE_SUCCESS,
    props<{
      data: any
    }>()
)

export const TrainAllAlertsByRouteFail = createAction(
    TRAIN_ALL_ALERTS_BY_ROUTE_FAIL,
    props<{
        error: any
    }>()
)

// alert by route
// uses TrainAllAlertsByRouteRequest interface because both just require route as the request
export const TrainAlertByRoute = createAction(
    TRAIN_ALERT_BY_ROUTE,
    props<{
        request: TrainAllAlertsByRouteRequest
    }>()
)

export const TrainAlertByRouteSuccess = createAction(
    TRAIN_ALERT_BY_ROUTE_SUCCESS,
    props<{
        data: any
    }>()
)

export const TrainAlertByRouteFail = createAction(
    TRAIN_ALERT_BY_ROUTE_FAIL,
    props<{
        error: any
    }>()
)

// alert by stop
export const TrainAlertByStop = createAction(
    TRAIN_ALERT_BY_STOP,
    props<{
        request: TrainAlertsByStopRequest
    }>()
)

export const TrainAlertByStopSuccess = createAction(
    TRAIN_ALERT_BY_STOP_SUCCESS,
    props<{
        data: any
    }>()
)

export const TrainAlertByStopFail = createAction(
    TRAIN_ALERT_BY_STOP_FAIL,
    props<{
        error: any
    }>()
)