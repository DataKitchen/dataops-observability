import { ChangeDetectionStrategy, Component, Input, Optional, Self } from '@angular/core';
import { NgControl } from '@angular/forms';
import { AbstractField } from '../abstract-field';
import { ThemePalette } from '@angular/material/core';


@Component({
  selector: 'checkbox-field',
  templateUrl: './checkbox-field.component.html',
  styleUrls: [ './checkbox-field.component.scss' ],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CheckboxFieldComponent extends AbstractField<boolean> {

  @Input() label!: string;
  @Input() info!: string;
  @Input() indeterminate!: boolean;
  @Input() color: ThemePalette = 'primary';

  constructor(
    @Self() @Optional() protected override ngControl: NgControl,
  ) {
    super(ngControl);
  }
}
