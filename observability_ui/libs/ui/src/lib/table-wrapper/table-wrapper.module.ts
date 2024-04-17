import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatLegacyCheckboxModule as MatCheckboxModule } from '@angular/material/legacy-checkbox';
import { MatDividerModule } from '@angular/material/divider';
import { FlexModule } from '@angular/flex-layout';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { MatIconModule } from '@angular/material/icon';
import { ReactiveFormsModule } from '@angular/forms';
import { MatLegacyProgressBarModule as MatProgressBarModule } from '@angular/material/legacy-progress-bar';
import { MatLegacyPaginatorModule as MatPaginatorModule } from '@angular/material/legacy-paginator';
import { MatLegacyCellDef as MatCellDef, MatLegacyColumnDef as MatColumnDef, MatLegacyHeaderCellDef as MatHeaderCellDef, MatLegacyTableModule as MatTableModule } from '@angular/material/legacy-table';
import { DragDropModule } from '@angular/cdk/drag-drop';
import { MatLegacyListModule as MatListModule } from '@angular/material/legacy-list';
import { MatLegacySlideToggleModule as MatSlideToggleModule } from '@angular/material/legacy-slide-toggle';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatSortModule } from '@angular/material/sort';
import { OverlayModule } from '@angular/cdk/overlay';
import { TranslationModule } from '@observability-ui/translate';
import { DkTooltipModule } from '../dk-tooltip';
import { translations } from './table-wrapper.translation';
import { TableWrapperComponent } from './table-wrapper.component';
import { SortDisabledDirective } from './sort-disabled.directive';
import { ToggleDisabledDirective } from './toggle-disabled.directive';
import { DragDisabledDirective } from './drag-disabled.directive';
import { HeaderLabelDirective } from './header-label.directive';
import { BindQueryParamsModule } from '../directives';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { MatLegacyInputModule as MatInputModule } from '@angular/material/legacy-input';
import { TableWrapperActionsComponent } from './table-wrapper-actions.component';


@NgModule({
  imports: [
    CommonModule,
    MatCheckboxModule,
    MatDividerModule,
    FlexModule,
    MatButtonModule,
    DkTooltipModule,
    MatIconModule,
    ReactiveFormsModule,
    MatProgressBarModule,
    MatPaginatorModule,
    MatTableModule,
    DragDropModule,
    MatListModule,
    MatSlideToggleModule,
    MatButtonToggleModule,
    MatSortModule,
    TranslationModule.forChild(translations),
    OverlayModule,
    BindQueryParamsModule,
    MatFormFieldModule,
    MatInputModule,
  ],
  exports: [
    TableWrapperComponent,
    SortDisabledDirective,
    ToggleDisabledDirective,
    DragDisabledDirective,
    HeaderLabelDirective,
    TableWrapperActionsComponent,
    MatColumnDef,
    MatHeaderCellDef,
    MatCellDef,
  ],
  declarations: [
    TableWrapperComponent,
    SortDisabledDirective,
    ToggleDisabledDirective,
    ToggleDisabledDirective,
    DragDisabledDirective,
    HeaderLabelDirective,
    TableWrapperActionsComponent,
  ],
  providers: [],
})
export class TableWrapperModule {
}
