import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { DkTooltipModule } from '../dk-tooltip';

@Component({
  selector: 'created-by',
  template: `
    <div [dkTooltip]="createdByTpl" [dkTooltipDisabled]="!enableTooltip">
      <ng-container [ngTemplateOutlet]="createdByTpl"></ng-container>
    </div>

    <ng-template #createdByTpl>
      Created by {{ createdBy?.name ?? 'system' }} <ng-container *ngIf="createdOn">on {{ createdOn | date: 'mediumDate' }}</ng-container>
    </ng-template>

  `,
  styles: [ `
      :host {
        display: flex;
        min-width: 0;
      }

      div {
        text-overflow: ellipsis;
        white-space: nowrap;
        overflow: hidden;
      }
  ` ],
  standalone: true,
  imports: [
    CommonModule,
    DkTooltipModule,
  ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CreatedByComponent {
  @Input() createdBy?: {id: string; name: string;};
  @Input() createdOn?: string;
  @Input() enableTooltip: boolean = false;
}
