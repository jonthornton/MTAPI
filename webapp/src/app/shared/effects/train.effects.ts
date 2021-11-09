import { Injectable } from '@angular/core';
import { createEffect, Actions, ofType } from '@ngrx/effects';
import { Observable ,  of } from 'rxjs';
import { map, switchMap, catchError } from 'rxjs/operators';
import * as trainActions from '../actions/train.actions';
import {AsyncTrainService} from "../services/async-train.service";

@Injectable()
export class TrainEffects {
  constructor(private actions: Actions,
              private trainService: AsyncTrainService) {}


  byLocation$ = createEffect(() => {
    return this.actions.pipe(
      ofType(trainActions.TRAIN_BY_LOCATION),
      switchMap(action => {
        return this.trainService.byLocation((action as any).request.lat,
          (action as any).request.lon
          ).pipe(
            map(byLocationResult => trainActions.TrainByLocationSuccess({data: byLocationResult})),
            catchError(byLocationError => of(trainActions.TrainByLocationFail({error: byLocationError.error})))
          )
      })
    )
  })

  byRoute$ = createEffect(() => {
    return this.actions.pipe(
      ofType(trainActions.TRAIN_BY_ROUTE),
      switchMap(action => {
        return this.trainService.byRoute((action as any).request.route).pipe(
          map(byRouteResult => trainActions.TrainByRouteSuccess({data: byRouteResult})),
          catchError(byRouteError => of(trainActions.TrainByRouteFail({error: byRouteError.error})))
        )
      })
    )
  })


  byIds$ = createEffect(() => {
    return this.actions.pipe(
      ofType(trainActions.TRAIN_BY_IDS),
      switchMap(action => {
        return this.trainService.byId((action as any).request.ids).pipe(
          map(byIdResult => trainActions.TrainByIdSuccess({data: byIdResult})),
          catchError(byIdError => of(trainActions.TrainByIdFail({error: byIdError.error})))
        )
      })
    )
  })


  routes$ = createEffect(() => {
    return this.actions.pipe(
      ofType(trainActions.TRAIN_ROUTES),
      switchMap(action => {
        return this.trainService.routes().pipe(
          map(routesResult => trainActions.TrainRoutesSuccess({data: routesResult})),
          catchError(routesError => of(trainActions.TrainRoutesFail({error: routesError.error})))
        )
      })
    )
  })
}
