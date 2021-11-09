import * as trainActions from '../../actions/train.actions';
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

const trainByRouteReducer = createReducer(
  initialState,
  on(trainActions.TrainByRoute, (state, {request}) => ({
    ...state,
    route: request.route
  })),
  on(trainActions.TrainByRouteSuccess, (state, {data}) => ({
    ...state,
    data: data
  })),
  on(trainActions.TrainByRouteFail, (state, {error}) => ({
    ...state,
    error: error
  }))
)

export function reducer(state: State | undefined, action: Action) {
  return trainByRouteReducer(state, action)
}
