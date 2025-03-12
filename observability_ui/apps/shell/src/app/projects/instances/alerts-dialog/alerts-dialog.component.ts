import { Component, Inject } from '@angular/core';
import { MAT_LEGACY_DIALOG_DATA as MAT_DIALOG_DATA, MatLegacyDialogModule } from '@angular/material/legacy-dialog';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { AsyncPipe, DatePipe, KeyValuePipe, NgFor, NgIf, NgSwitch, NgSwitchCase, NgSwitchDefault, TitleCasePipe } from '@angular/common';
import { DkTooltipModule, DurationModule, FilterFieldModule, TableChangeEvent, TableWrapperModule } from '@observability-ui/ui';
import { TranslationModule } from '@observability-ui/translate';
import { InstancesStore } from '../../../stores/instances/instances.store';
import { takeUntilDestroyed, toSignal } from '@angular/core/rxjs-interop';
import { AlertsSearchFields, Instance, InstanceAlertType, RunAlertType } from '@observability-ui/core';
import { TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { map, Subject } from 'rxjs';
import { MatIconModule } from '@angular/material/icon';
import { ReactiveFormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { InstanceAlertsComponent } from '../instance-alerts/instance-alerts.component';

@Component({
  selector: 'shell-alerts-dialog',
  standalone: true,
  imports: [
    MatLegacyDialogModule,
    MatLegacyButtonModule,
    AsyncPipe,
    TableWrapperModule,
    TranslationModule,
    DatePipe,
    KeyValuePipe,
    NgFor,
    NgSwitchCase,
    NgSwitch,
    NgSwitchDefault,
    NgIf,
    MatIconModule,
    ReactiveFormsModule,
    FilterFieldModule,
    TitleCasePipe,
    RouterLink,
    DurationModule,
    InstanceAlertsComponent,
    DkTooltipModule
  ],
  templateUrl: 'alerts-dialog.component.html',
  styleUrls: [ 'alerts-dialog.component.scss' ]
})

export class AlertsDialogComponent {
  loading = toSignal(this.store.getLoadingFor('getAlertsByPage'));
  alerts = toSignal(this.store.instanceAlerts$);
  total = toSignal(this.store.instanceAlertsTotal$);
  components = toSignal(this.store.components$);

  RunAlertType = RunAlertType;

  alertTypes = [ // Sort conceptually
    RunAlertType.Failed,
    RunAlertType.CompletedWithWarnings,
    InstanceAlertType.LateStart,
    InstanceAlertType.LateEnd,
    RunAlertType.MissingRun,
    RunAlertType.UnexpectedStatusChange,
    InstanceAlertType.DatasetNotReady,
    InstanceAlertType.TestsFailed,
    InstanceAlertType.TestsHadWarnings,
    InstanceAlertType.Incomplete,
    InstanceAlertType.OutOfSequence,
  ];

  search = new TypedFormGroup<AlertsSearchFields>({
    type: new TypedFormControl<string>(),
    component_id: new TypedFormControl<string>()
  });

  tableChange$ = new Subject<TableChangeEvent<AlertsSearchFields>>();

  constructor(@Inject(MAT_DIALOG_DATA) public data: {
    projectId: string,
    instanceId: string,
    journeyId: string,
    instance: Instance
  }, private store: InstancesStore, private router: Router) {
    let urlTree = this.router.parseUrl(this.router.url);
    urlTree.queryParams['_pageSize'] = '25';
    urlTree.queryParams['_pageIndex'] = 0;

    void this.router.navigateByUrl(urlTree);

    this.store.dispatch('findComponents', this.data.journeyId);

    this.tableChange$.pipe(
      takeUntilDestroyed(),
      map(({ search, ...page }) => {
        return {
          ...page,
          search: {
            type: search.type?.split(',')?.filter(n => n) || [],
            component_id: search.component_id?.split(',')?.filter(n => n) || []
          }
        };
      })
    ).subscribe(({ pageIndex: page, pageSize: count, search: filters }) => {
      this.store.dispatch('getAlertsByPage', this.data.projectId, this.data.instanceId, {
        page,
        count,
        sort: 'desc',
        filters: filters as any
      });
    });
  }

  onTableChange(page: TableChangeEvent<AlertsSearchFields>) {
    this.tableChange$.next(page);
  }
}
