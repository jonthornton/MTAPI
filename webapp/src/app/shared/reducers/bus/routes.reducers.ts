import * as busActions from '../../actions/bus.actions';
import {Action, createReducer, on} from "@ngrx/store";

export interface State {
  data: any,
  error: any
}

export const initialState: State = {
  data: {},
  error: ""
}

const busRoutesReducer = createReducer(
  initialState,
  on(busActions.BusRoutes, (state, {}) => ({
    ...state
  })),
  on(busActions.BusRoutesSuccess, (state, {data}) => ({
    ...state,
    data: data
  })),
  on(busActions.BusRoutesFail, (state, {error}) => ({
    ...state,
    error: error
  }))
)

export function reducer(state: State | undefined, action: Action) {
  return busRoutesReducer(state, action)
}
