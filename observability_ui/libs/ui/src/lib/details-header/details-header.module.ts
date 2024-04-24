import { NgModule } from '@angular/core';
import { DetailsHeaderComponent } from './details-header.component';
import { TruncateModule } from '../truncate';
import { DkTooltipModule } from '../dk-tooltip';
import { NgIf } from '@angular/common';
import { FlexModule } from '@angular/flex-layout';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';

@NgModule({
  imports: [
    TruncateModule,
    DkTooltipModule,
    NgIf,
    FlexModule,
    RouterModule,
    MatIconModule
  ],
  exports: [
    DetailsHeaderComponent,
  ],
  declarations: [
    DetailsHeaderComponent,
  ],
  providers: [],
})
export class DetailsHeaderModule {}
