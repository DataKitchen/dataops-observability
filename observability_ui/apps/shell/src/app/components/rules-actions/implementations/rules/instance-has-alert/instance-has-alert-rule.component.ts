import { Component } from '@angular/core';
import { AbstractRule } from '../../../abstract.rule';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { CommonModule } from '@angular/common';
import { FormControl, FormGroup, ReactiveFormsModule } from '@angular/forms';
import { RuleType } from '../../../rule.model';
import { RunsModule } from '../../../../../projects/runs/runs.module';
import { FilterFieldModule } from '@observability-ui/ui';
import { InstanceAlertType } from '@observability-ui/core';

/**
 * For instance alerts:
 * When <instance has alert> of type <selected instance alert types>, <do action>
 *
 * Examples:
 *
 * When instance has alert “out of sequence,” <do action>
 *
 * When instance has alert “incomplete,” <do action>
 */

@Component({
  // eslint-disable-next-line @angular-eslint/component-selector
  selector: 'instance-has-alert-rule',
  template: `
    <ng-container *ngIf="editMode; else displayMode">

      <div class="line">
        <span>of type</span>

        <mat-select [formControl]="alertType" multiple="true">

<!--          <mat-option (click)="onSelectAll();">{{'selectAll' | translate}}</mat-option>-->
          <mat-optgroup *ngFor="let group of typeGroups" [label]="group.name">
            <mat-option class="mat-primary" *ngFor="let type of group.types" [value]="type">
              {{ labels[type] }}
            </mat-option>
          </mat-optgroup>
        </mat-select>
      </div>
    </ng-container>

    <ng-template #displayMode>
      <span>When {{labelFromInstance}} of type</span>
      <ng-container *ngFor="let type of alertType.value; let i = index">
        <code>
          {{ labels[type] }}
        </code>
        <span *ngIf="i < alertType.value?.length - 2">,</span>
        <span *ngIf="i === alertType.value?.length - 2">or</span>
      </ng-container>

    </ng-template>
  `,
  styles: [ `
    :host {
      display: flex;
      flex-direction: row;
      align-items: center;
    }
  ` ],
  imports: [
    ReactiveFormsModule,
    MatSelectModule,
    CommonModule,
    RunsModule,
    FilterFieldModule,
  ],
  standalone: true,
})
export class InstanceHasAlertRuleComponent extends AbstractRule {

  static override label: string = 'instance has alert';
  static override _type: RuleType = 'instance_alert';
  static override showComponentSelection = false;

  labels = {
    [InstanceAlertType.LateStart]: 'Late Start',
    [InstanceAlertType.LateEnd]: 'Late End',
    [InstanceAlertType.Incomplete]: 'Incomplete',
    [InstanceAlertType.OutOfSequence]: 'Out of sequence',
    [InstanceAlertType.DatasetNotReady]: 'Dataset not ready'
  };

  typeGroups: {name: string, types: (InstanceAlertType|number)[]}[] = [
    {
      name: 'Error',
      types: [ InstanceAlertType.Incomplete, InstanceAlertType.OutOfSequence ],
    },
    {
      name: 'Warning',
      types: [ InstanceAlertType.DatasetNotReady ],
    },
  ];

  alertType = new FormControl<(InstanceAlertType | number)[] | null>(null);

  /**
   *
   *  "instance_alert": {
   *       // Support only one of these fields at a time?
   *       "level": [...list of alert levels (empty implies "any")...],
   *       "type": [...list of alert types...]
   *   }
   *
   * However we won't provide a level field and the BE will assume "any"
   */
  form = new FormGroup({
    type_matches: this.alertType,
  });

  // onSelectAll() {
  //   this.alertType.patchValue([ ...this.typeGroups[0].types, ...this.typeGroups[1].types ]);
  // }
}
