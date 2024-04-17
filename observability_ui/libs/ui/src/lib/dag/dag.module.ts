import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { DagComponent } from './dag.component';
import { DagNodeDirective } from './dag-node.directive';
import { DagEdgeDirective } from './dag-edge.directive';
import { TranslationModule } from '@observability-ui/translate';
import { dagTranslations } from './dag.translation';
import { MatLegacyProgressSpinnerModule as MatProgressSpinnerModule } from '@angular/material/legacy-progress-spinner';
import { DagActionsComponent } from './dag-actions/dag-actions.component';
import { MatIconModule } from '@angular/material/icon';
import { DkTooltipModule } from '../dk-tooltip';
import { DagLegendDirective } from './dag-legend.directive';


@NgModule({
  imports: [
    CommonModule,
    MatIconModule,
    MatProgressSpinnerModule,
    DkTooltipModule,
    TranslationModule.forChild(dagTranslations),
  ],
  exports: [
    DagComponent,
    DagNodeDirective,
    DagEdgeDirective,
    DagActionsComponent,
    DagLegendDirective,
  ],
  declarations: [
    DagComponent,
    DagNodeDirective,
    DagEdgeDirective,
    DagActionsComponent,
    DagLegendDirective,
  ],
  providers: [],
})
export class DagModule {}
