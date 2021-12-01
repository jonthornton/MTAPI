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

const busAlertByRouteReducer = createReducer(
    initialState,
    on(busActions.BusAlertByRoute, (state, {request}) => ({
        ...state,
        route: request.route
    })),
    on(busActions.BusAlertByRouteSuccess, (state, {data}) => ({
        ...state,
        data: data
    })),
    on(busActions.BusAlertByRouteFail, (state, {error}) => ({
        ...state,
        error: error
    }))
)

export function reducer(state: State | undefined, action: Action) {
    return busAlertByRouteReducer(state, action);
}