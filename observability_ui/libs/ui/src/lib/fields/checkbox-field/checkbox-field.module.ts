import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatLegacyCheckboxModule as MatCheckboxModule } from '@angular/material/legacy-checkbox';
import { MatIconModule } from '@angular/material/icon';
import { ReactiveFormsModule } from '@angular/forms';
import { DkTooltipModule } from '../../dk-tooltip/dk-tooltip.module';
import { CheckboxFieldComponent } from './checkbox-field.component';

@NgModule({
  imports: [
    CommonModule,
    DkTooltipModule,
    MatCheckboxModule,
    MatIconModule,
    ReactiveFormsModule,
  ],
  exports: [ CheckboxFieldComponent ],
  declarations: [ CheckboxFieldComponent ],
})
export class CheckboxFieldModule {
}
