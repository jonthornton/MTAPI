import * as busActions from '../../actions/bus.actions';
import {Action, createReducer, on} from "@ngrx/store";

export interface State {
  lat: number,
  lon: number,
  num: number,
  data: any,
  error: any
}

export const initialState: State = {
  lat: 0,
  lon: 0,
  num: 0,
  data: {},
  error: ""
}

const busByLocationReducer = createReducer(
  initialState,
  on(busActions.BusByLocation, (state, {request}) => ({
    ...state,
    lat: request.lat,
    lon: request.lon,
    num: request.num
  })),
  on(busActions.BusByLocationSuccess, (state, {data}) => ({
    ...state,
    data: data
  })),
  on(busActions.BusByLocationFail, (state, {error}) => ({
    ...state,
    error: error
  }))
)

export function reducer(state: State | undefined, action: Action) {
  return busByLocationReducer(state, action)
}
