import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { MatLegacyCardModule } from '@angular/material/legacy-card';
import { AsyncPipe, NgIf, NgTemplateOutlet } from '@angular/common';
import { DkTooltipModule } from '../dk-tooltip';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { AbstractField } from '../fields';
import { TypedFormGroup } from '@datakitchen/ngx-toolkit';

@Component({
  selector: 'mat-card-edit',
  templateUrl: 'mat-card-edit.component.html',
  styleUrls: ['mat-card-edit.component.scss'],
  standalone: true,
  imports: [
    MatLegacyCardModule,
    AsyncPipe,
    NgTemplateOutlet,
    DkTooltipModule,
    MatIconModule,
    MatLegacyButtonModule,
    NgIf
  ]
})
export class MatCardEditComponent extends AbstractField implements OnChanges {
  @Input() title!: string;
  @Input() editing!: boolean;
  @Input() iconTooltip!: string;
  @Input() saving!: boolean;
  @Input() formGroup!: TypedFormGroup<any>;

  @Output() save: EventEmitter<void> = new EventEmitter<void>();
  @Output() cancel: EventEmitter<void> = new EventEmitter<void>();

  ngOnChanges({saving}: SimpleChanges): void {

    // assuming that when saving changes from true to false
    // means that a save operation ended up successfully.
    if (saving && !saving.firstChange && saving.previousValue === true && saving.currentValue === false) {
      this.editing = false;
    }

  }

  toggleEdit() {
    this.editing = !this.editing;
  }

  onSave() {
    this.save.emit();
  }

  onCancel() {
    this.cancel.emit();
  }
}
