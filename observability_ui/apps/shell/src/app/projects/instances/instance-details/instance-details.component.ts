import { Component, OnDestroy, effect } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { MatLegacyDialog } from '@angular/material/legacy-dialog';
import { ActivatedRoute } from '@angular/router';
import { Instance } from '@observability-ui/core';
import { map } from 'rxjs';
import { InstancesStore } from '../../../stores/instances/instances.store';
import { AlertsDialogComponent } from '../alerts-dialog/alerts-dialog.component';

@Component({
  selector: 'shell-instance-details',
  templateUrl: './instance-details.component.html',
  styleUrls: [ './instance-details.component.scss' ]
})
export class InstanceDetailsComponent implements OnDestroy {
  instance$ = this.store.selected$;

  private instanceId = toSignal(
    this.route.params.pipe(
      map(({ id }) => id)
    )
  );

  private projectId = toSignal(
    this.route.params.pipe(
      map(({ projectId }) => projectId)
    )
  );

  constructor(private route: ActivatedRoute, private store: InstancesStore, private matDialog: MatLegacyDialog) {

    effect(() => {
      const instanceId = this.instanceId();
      if (instanceId) {
        this.store.dispatch('getOne', instanceId);
      }
    });
  }

  public ngOnDestroy(): void {
    this.store.dispatch('reset');
  }

  openAlertsDialog(instance: Instance) {
    this.matDialog.open(AlertsDialogComponent, {
      width: '80%',
      data: {
        instanceId: instance.id,
        projectId: this.projectId(),
        journeyId: instance.journey.id,
        instance: instance
      }
    });
  }
}
