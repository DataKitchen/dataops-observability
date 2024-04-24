import { NgModule } from '@angular/core';
import { EntityListPlaceholderComponent } from './entity-list-placeholder/entity-list-placeholder.component';
import { CommonModule } from '@angular/common';
import { MatLegacyProgressSpinnerModule as MatProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { TranslationModule } from '@observability-ui/translate';
import { ActiveStatusChipComponent } from './active-status-chip/active-status-chip.component';
import { NullifyPendingPipe } from './nullify-pending/nullify-pending.pipe';

const exportables = [
  EntityListPlaceholderComponent,
  ActiveStatusChipComponent,
  NullifyPendingPipe,
];

@NgModule({
  imports: [
    CommonModule,
    MatProgressSpinnerModule,
    TranslationModule.forChild(),
  ],
  exports: [
    exportables,
  ],
  declarations: [
    exportables,
  ],
  providers: [],
})
export class  EntityModule {
}
