import * as busActions from '../../actions/bus.actions';
import {Action, createReducer, on} from "@ngrx/store";

export interface State {
  route: string,
  data: any,
  error: any
}

export const initialState: State = {
  route: "",
  data: {},
  error: ""
}

const busByRouteReducer = createReducer(
  initialState,
  on(busActions.BusByRoute, (state, {request}) => ({
    ...state,
    route: request.route
  })),
  on(busActions.BusByRouteSuccess, (state, {data}) => ({
    ...state,
    data: data
  })),
  on(busActions.BusByRouteFail, (state, {error}) => ({
    ...state,
    error: error
  }))
)

export function reducer(state: State | undefined, action: Action) {
  return busByRouteReducer(state, action)
}
