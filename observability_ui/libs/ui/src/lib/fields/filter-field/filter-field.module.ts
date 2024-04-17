import { forwardRef, NgModule } from '@angular/core';
import { FilterFieldComponent } from './filter-field.component';
import { FormGroupDirective, NG_VALUE_ACCESSOR, ReactiveFormsModule } from '@angular/forms';
import { FullscreenOverlayContainer, OverlayContainer, OverlayModule } from '@angular/cdk/overlay';
import { FilterFieldOptionComponent } from './filter-field-option.component';
import { DkTooltipModule } from '../../dk-tooltip/dk-tooltip.module';
import { MatRippleModule } from '@angular/material/core';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';
import { FlexModule } from '@angular/flex-layout';
import { TranslationModule } from '@observability-ui/translate';
import { MatLegacyCheckboxModule as MatCheckboxModule } from '@angular/material/legacy-checkbox';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { TruncateModule } from '../../truncate';
import { MatLegacyProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';

@NgModule({
  imports: [
    OverlayModule,
    DkTooltipModule,
    MatRippleModule,
    CommonModule,
    MatIconModule,
    FlexModule,
    ReactiveFormsModule,
    TranslationModule,
    MatCheckboxModule,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    TruncateModule,
    MatLegacyProgressSpinnerModule
  ],
  exports: [
    FilterFieldComponent,
    FilterFieldOptionComponent,
    FormGroupDirective,
  ],
  declarations: [
    FilterFieldComponent,
    FilterFieldOptionComponent,
  ],
  providers: [
    {
      provide: NG_VALUE_ACCESSOR,
      useExisting: forwardRef(() => FilterFieldComponent),
      multi: true
    },
    // Use fullscreen-compatible overlays - https://material.angular.io/cdk/overlay/overview#full-screen-overlays
    // Needed for fullscreen editing of variation graph
    { provide: OverlayContainer, useClass: FullscreenOverlayContainer },
  ]
})
export class FilterFieldModule {
}
