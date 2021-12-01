import * as trainActions from '../../actions/train.actions';
import {Action, createReducer, on} from "@ngrx/store";

export interface State {
    stop: string,
    data: any,
    error: any
}

export const initialState: State = {
    stop: "",
    data: {},
    error: ""
}

const trainAlertByStopReducer = createReducer(
    initialState,
    on(trainActions.TrainAlertByStop, (state, {request}) => ({
        ...state,
        route: request.stop
    })),
    on(trainActions.TrainAlertByStopSuccess, (state, {data}) => ({
        ...state,
        data: data
    })),
    on(trainActions.TrainAlertByStopFail, (state, {error}) => ({
        ...state,
        error: error
    }))
)

export function reducer(state: State | undefined, action: Action) {
    return trainAlertByStopReducer(state, action);
}