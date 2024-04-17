import { NgModule } from '@angular/core';
import { PortalModule } from '@angular/cdk/portal';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';
import { FlexModule } from '@angular/flex-layout';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { Overlay } from '@angular/cdk/overlay';
import { DkTooltipDirective } from './dk-tooltip.directive';
import { DkTooltipComponent } from './dk-tooltip.component';

@NgModule({
  imports: [
    CommonModule,
    FlexModule,
    MatIconModule,
    MatButtonModule,
    PortalModule,
  ],
  exports: [ DkTooltipDirective ],
  declarations: [
    DkTooltipDirective,
    DkTooltipComponent,
  ],
  providers: [ Overlay ],
})
export class DkTooltipModule {
}
