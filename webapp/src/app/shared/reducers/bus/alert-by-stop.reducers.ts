import * as busActions from '../../actions/bus.actions';
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

const busAlertByStopReducer = createReducer(
    initialState,
    on(busActions.BusAlertByStop, (state, {request}) => ({
        ...state,
        route: request.stop
    })),
    on(busActions.BusAlertByStopSuccess, (state, {data}) => ({
        ...state,
        data: data
    })),
    on(busActions.BusAlertByStopFail, (state, {error}) => ({
        ...state,
        error: error
    }))
)

export function reducer(state: State | undefined, action: Action) {
    return busAlertByStopReducer(state, action);
}