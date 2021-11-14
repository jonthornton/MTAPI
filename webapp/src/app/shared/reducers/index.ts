import * as fromTrainByLocation from './train/by-location.reducers';
import * as fromTrainByRoute from './train/by-route.reducers';
import * as fromTrainById from './train/by-ids.reducers';
import * as fromTrainRoutes from './train/routes.reducers';

import * as fromBusByLocation from './bus/by-location.reducers';
import * as fromBusByRoute from './bus/by-route.reducers';
import * as fromBusById from './bus/by-ids.reducers';
import * as fromBusRoutes from './bus/routes.reducers';

export const reducers = {
  trainByLocation: fromTrainByLocation.reducer,
  trainByRoute: fromTrainByRoute.reducer,
  trainById: fromTrainById.reducer,
  trainRoutes: fromTrainRoutes.reducer,

  busByLocation: fromBusByLocation.reducer,
  busByRoute: fromBusByRoute.reducer,
  busById: fromBusById.reducer,
  busRoutes: fromBusRoutes.reducer
}
