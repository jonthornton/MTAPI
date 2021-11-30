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

const trainAllAlertsByRouteReducer = createReducer(
    initialState,
    on(trainActions.TrainAllAlertsByRoute, (state, {request}) => ({
        ...state,
        route: request.route
    })),
    on(trainActions.TrainAllAlertsByRouteSuccess, (state, {data}) => ({
        ...state,
        data: data
    })),
    on(trainActions.TrainAllAlertsByRouteFail, (state, {error}) => ({
        ...state,
        error: error
    }))
)

export function reducer(state: State | undefined, action: Action) {
    return trainAllAlertsByRouteReducer(state, action);
}