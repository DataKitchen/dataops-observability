import { NgModule } from '@angular/core';
import { TimespanFieldComponent } from './timespan-field.component';
import { TextFieldModule } from '../text-field/text-field.module';
import { TranslationModule } from '@observability-ui/translate';
import { ReactiveFormsModule } from '@angular/forms';
import { MatLegacySelectModule } from '@angular/material/legacy-select';
import { MatLegacyFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacyButtonModule } from '@angular/material/legacy-button';
import { TimespanPipe } from './timespan.pipe';
import { timespanTranslation } from './timespan.translation';

@NgModule({
  declarations: [
    TimespanFieldComponent,
    TimespanPipe
  ],
  exports: [
    TimespanFieldComponent,
    TimespanPipe
  ],
  imports: [
    MatLegacyFormFieldModule,
    TextFieldModule,
    MatLegacySelectModule,
    TranslationModule.forChild({
      ...timespanTranslation
    }),
    ReactiveFormsModule,
    MatLegacyButtonModule
  ]
})
export class TimespanFieldModule {
}
