import * as trainActions from '../../actions/train.actions';
import {Action, createReducer, on} from "@ngrx/store";

export interface State {
  lat: number,
  lon: number,
  data: any,
  error: any
}

export const initialState: State = {
  lat: 0,
  lon: 0,
  data: {},
  error: ""
}

const trainByLocationReducer = createReducer(
  initialState,
  on(trainActions.TrainByLocation, (state, {request}) => ({
    ...state,
    lat: request.lat,
    lon: request.lon
  })),
  on(trainActions.TrainByLocationSuccess, (state, {data}) => ({
    ...state,
    data: data
  })),
  on(trainActions.TrainByLocationFail, (state, {error}) => ({
    ...state,
    error: error
  }))
)

export function reducer(state: State | undefined, action: Action) {
  return trainByLocationReducer(state, action)
}
