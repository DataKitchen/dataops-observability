import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { DatasetOperationEventData, EventType, EventTypes, MessageLogEventData, ProjectStore, RunProcessedStatus, RunStatusEventData, TestOutcomesEventData, TestStatus } from '@observability-ui/core';
import { MetadataViewerComponent, MetadataViewerData, TableChangeEvent } from '@observability-ui/ui';
import { MatLegacyDialog as MatDialog } from '@angular/material/legacy-dialog';
import { FormGroup } from '@angular/forms';
import { BehaviorSubject, map } from 'rxjs';
import { CoreComponent, omit } from '@datakitchen/ngx-toolkit';
import { toSignal } from '@angular/core/rxjs-interop';

@Component({
  selector: 'shell-events-table',
  templateUrl: './events-table.component.html',
  styleUrls: [ './events-table.component.scss' ]
})
export class EventsTableComponent extends CoreComponent implements OnInit {
  protected readonly RunProcessedStatus = RunProcessedStatus;
  protected readonly EventTypes = EventTypes;

  projectId = toSignal(this.projectStore.current$.pipe(map(({ id }) => id)));

  @Input() set items(events: EventType[]) {
    this.items$.next(this.getEventsWithTestSummary(this.addComponentKeys(events)));
  }

  @Input()
  columns: any[] = [ 'timestamp', 'component', { name: 'component_key', visible: false }, { name: 'task_key', visible: false }, 'event_type', 'details' ];

  @Input()
  public total!: number;

  @Input()
  public loading!: boolean;

  @Output()
  public tableChange: EventEmitter<TableChangeEvent> = new EventEmitter<TableChangeEvent>();

  @Input()
  public search!: FormGroup;

  public items$: BehaviorSubject<EventType[]> = new BehaviorSubject<EventType[]>([]);


  constructor(
    private matDialog: MatDialog,
    private projectStore: ProjectStore,
  ) {
    super();
  }

  override ngOnInit() {
    super.ngOnInit();
  }

  viewMetadata(event: EventType): void {
    this.matDialog.open<MetadataViewerComponent, MetadataViewerData>(MetadataViewerComponent, {
      minWidth: 500,
      maxWidth: 500,
      minHeight: 200,
      data: {
        title: 'Event Data',
        all: omit(event, [ 'component_key', 'summary' ]),
        timestamp: event.timestamp,
        metadata: event.raw_data.metadata ?? {},
      }
    });
  }

  addComponentKeys(events: EventType[]): EventType[] {
    return events.map((event) => {
      if (event.event_type === EventTypes.RunStatusEvent) {
        const { batch_pipeline_component } = event.raw_data as RunStatusEventData;
        return { ...event, component_key: batch_pipeline_component.batch_key, task_key: batch_pipeline_component.task_key };
      } else if (event.event_type === EventTypes.DatasetOperationEvent) {
        return { ...event, component_key: (event.raw_data as DatasetOperationEventData).dataset_component.dataset_key };
      } else {
        const { batch_pipeline, dataset, server, stream } = (event.raw_data as MessageLogEventData).component;
        return {
          ...event,
          component_key: batch_pipeline?.batch_key || dataset?.dataset_key || server?.server_key || stream?.stream_key,
          task_key: batch_pipeline?.task_key,
        };
      }
    });
  }

  getEventsWithTestSummary(events: EventType[]): EventType[] {
    return events.map((event) => {
      // Test outcomes
      if (event.event_type === EventTypes.TestOutcomesEvent) {
        const summary = { [TestStatus.Passed]: 0, [TestStatus.Warning]: 0, [TestStatus.Failed]: 0, TOTAL: 0 };
        for (const result of ((event.raw_data as TestOutcomesEventData).test_outcomes || [])) {
          summary[result.status as TestStatus] += 1;
        }

        summary.TOTAL = summary[TestStatus.Passed] + summary[TestStatus.Warning] + summary[TestStatus.Failed];
        return { ...event, summary };
      }

      return event;
    });
  }

}
