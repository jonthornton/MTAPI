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

const busAllAlertsByRouteReducer = createReducer(
    initialState,
    on(busActions.BusAllAlertsByRoute, (state, {request}) => ({
        ...state,
        route: request.route
    })),
    on(busActions.BusAllAlertsByRouteSuccess, (state, {data}) => ({
        ...state,
        data: data
    })),
    on(busActions.BusAllAlertsByRouteFail, (state, {error}) => ({
        ...state,
        error: error
    }))
)

export function reducer(state: State | undefined, action: Action) {
    return busAllAlertsByRouteReducer(state, action);
}