import { Component, Input } from '@angular/core';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'templating-alert',
  styleUrls: [ 'templating-alert.component.scss' ],
  template: `
    <ng-container *ngIf="editing else editTemplate">
      <mat-icon dkTooltip="{{alert}}">{{alertIcon}}</mat-icon>
    </ng-container>
    <ng-template #editTemplate>
      <div class="flex-row">
        <mat-icon>{{alertIcon}}</mat-icon>
        <span class="ml-1">{{alert}}</span>
      </div>
    </ng-template>
  `,
})
export class TemplatingAlertComponent {
  @Input() alert: string;
  @Input() alertIcon: string;
  @Input() editing: boolean = false;
}
