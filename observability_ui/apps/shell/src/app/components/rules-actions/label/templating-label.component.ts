import { Component, Input } from '@angular/core';
import { AbstractTemplating } from '../abstract-templating.directive';

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'templating-label',
  template: `
    <ng-container *ngIf="component.label; else labelTpl">
      <mat-icon *ngIf="component.icon">{{component.icon}}</mat-icon>
      {{component.label}}
    </ng-container>
    <ng-template #labelTpl>
      <ng-container
        *dynamicComponentOutlet="component.labelTpl"></ng-container>
    </ng-template>
  `,
})
export class TemplatingLabelComponent {
  @Input() component: typeof AbstractTemplating;
}
