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

const busByIdReducer = createReducer(
  initialState,
  on(busActions.BusById, (state, {request}) => ({
    ...state,
    ids: request.ids
  })),
  on(busActions.BusByIdSuccess, (state, {data}) => ({
    ...state,
    data: data
  })),
  on(busActions.BusByIdFail, (state, {error}) => ({
    ...state,
    error: error
  }))
)

export function reducer(state: State | undefined, action: Action) {
  return busByIdReducer(state, action)
}
