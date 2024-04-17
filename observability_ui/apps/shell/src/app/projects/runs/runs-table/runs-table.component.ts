import { Component, EventEmitter, Input, Output } from '@angular/core';
import { Run, RunAlertType, RunProcessedStatus } from '@observability-ui/core';
import { CoreComponent, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { TableChangeEvent } from '@observability-ui/ui';

@Component({
  selector: 'shell-runs-table',
  templateUrl: 'runs-table.component.html',
  styleUrls: [ 'runs-table.component.scss' ]
})

export class RunsTableComponent extends CoreComponent {
  @Input() items: Run[];

  @Input()
  public total!: number;

  @Input()
  public loading!: boolean;

  @Input()
  public search!: TypedFormGroup<any>;

  @Output()
  public tableChange: EventEmitter<TableChangeEvent> = new EventEmitter<TableChangeEvent>();

  public runStatus = RunProcessedStatus;

  protected readonly RunAlertType = RunAlertType;
}
