import * as trainActions from '../../actions/train.actions';
import {Action, createReducer, on} from "@ngrx/store";

export interface State {
  data: any,
  error: any
}

export const initialState: State = {
  data: {},
  error: ""
}

const trainRoutesReducer = createReducer(
  initialState,
  on(trainActions.TrainRoutes, (state, {}) => ({
    ...state
  })),
  on(trainActions.TrainRoutesSuccess, (state, {data}) => ({
    ...state,
    data: data
  })),
  on(trainActions.TrainRoutesFail, (state, {error}) => ({
    ...state,
    error: error
  }))
)

export function reducer(state: State | undefined, action: Action) {
  return trainRoutesReducer(state, action)
}
