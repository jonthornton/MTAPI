import * as fromTrainByLocation from './train/by-location.reducers';
import * as fromTrainByRoute from './train/by-route.reducers';
import * as fromTrainById from './train/by-ids.reducers';
import * as fromTrainRoutes from './train/routes.reducers';
import * as fromTrainAllAlertsByRoute from './train/all-alerts-by-route.reducers';
import * as fromTrainAlertByRoute from './train/alert-by-route.reducers';
import * as fromTrainAlertByStop from './train/alert-by-stop.reducers';

import * as fromBusByLocation from './bus/by-location.reducers';
import * as fromBusByRoute from './bus/by-route.reducers';
import * as fromBusById from './bus/by-ids.reducers';
import * as fromBusRoutes from './bus/routes.reducers';
import * as fromBusAllAlertsByRoute from './bus/all-alerts-by-route.reducers';
import * as fromBusAlertByRoute from './bus/alert-by-route.reducers';
import * as fromBusAlertByStop from './bus/alert-by-stop.reducers';

export const reducers = {
  trainByLocation: fromTrainByLocation.reducer,
  trainByRoute: fromTrainByRoute.reducer,
  trainById: fromTrainById.reducer,
  trainRoutes: fromTrainRoutes.reducer,
  trainAllAlertsByRoute: fromTrainAllAlertsByRoute.reducer,
  trainAlertByRoute: fromTrainAlertByRoute.reducer,
  trainAlertByStop: fromTrainAlertByStop.reducer,

  busByLocation: fromBusByLocation.reducer,
  busByRoute: fromBusByRoute.reducer,
  busById: fromBusById.reducer,
  busRoutes: fromBusRoutes.reducer,
  busAllAlertsByRoute: fromBusAllAlertsByRoute.reducer,
  busAlertByRoute: fromBusAlertByRoute.reducer,
  busAlertByStop: fromBusAlertByStop.reducer
}
