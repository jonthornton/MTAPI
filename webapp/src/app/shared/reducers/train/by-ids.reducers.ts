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

const trainByIdReducer = createReducer(
  initialState,
  on(trainActions.TrainById, (state, {request}) => ({
    ...state,
    ids: request.ids
  })),
  on(trainActions.TrainByIdSuccess, (state, {data}) => ({
    ...state,
    data: data
  })),
  on(trainActions.TrainByIdFail, (state, {error}) => ({
    ...state,
    error: error
  }))
)

export function reducer(state: State | undefined, action: Action) {
  return trainByIdReducer(state, action)
}
