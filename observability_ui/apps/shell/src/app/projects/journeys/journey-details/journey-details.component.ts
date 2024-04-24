import { Component } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { map, switchMap, tap } from 'rxjs';
import { JourneysStore } from '../journeys.store';

@Component({
  selector: 'shell-journey-details',
  templateUrl: './journey-details.component.html',
  styleUrls: [ 'journey-details.component.scss' ],
})
export class JourneyDetailsComponent {

  journeyId$ =  this.route.params.pipe(
    map(({id}) => id),
    tap((id) => {
      this.store.dispatch('getOne', id);
      this.store.dispatch('findComponents', id);
    })
  );

  journey$ = this.journeyId$.pipe(
    switchMap((id) => {
      return this.store.getEntity(id);
    })
  );
  componentKeys$ = this.store.components$.pipe(
    map(components => components.map(c => c.key).join(',')),
  );

  constructor(
    private route: ActivatedRoute,
    private store: JourneysStore) {
  }

}
