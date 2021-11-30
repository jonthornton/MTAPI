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

const trainAlertByRouteReducer = createReducer(
    initialState,
    on(trainActions.TrainAlertByRoute, (state, {request}) => ({
        ...state,
        route: request.route
    })),
    on(trainActions.TrainAlertByRouteSuccess, (state, {data}) => ({
        ...state,
        data: data
    })),
    on(trainActions.TrainAlertByRouteFail, (state, {error}) => ({
        ...state,
        error: error
    }))
)

export function reducer(state: State | undefined, action: Action) {
    return trainAlertByRouteReducer(state, action);
}