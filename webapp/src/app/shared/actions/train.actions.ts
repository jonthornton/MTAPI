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

/*
need to figure out with variable number of args...maybe just array
export interface TrainByIdRequest {
   ids: any[]
}
 */

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
