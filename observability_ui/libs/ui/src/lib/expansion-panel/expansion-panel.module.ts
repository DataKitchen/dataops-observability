import { NgModule } from '@angular/core';
import { ExpansionPanelComponent } from './expansion-panel/expansion-panel.component';
import { MatIconModule } from '@angular/material/icon';
import { ExpansionPanelTitleComponent } from './expansion-panel-title/expansion-panel-title.component';
import { CommonModule } from '@angular/common';
import { ExpansionPanelContentComponent } from './expansion-panel-content/expansion-panel-content.component';
import { FlexModule } from '@angular/flex-layout';

@NgModule({
  imports: [
    MatIconModule,
    CommonModule,
    FlexModule
  ],
  exports: [
    ExpansionPanelComponent,
    ExpansionPanelTitleComponent,
    ExpansionPanelContentComponent,
  ],
  declarations: [
    ExpansionPanelComponent,
    ExpansionPanelTitleComponent,
    ExpansionPanelContentComponent,
  ],
  providers: [],
})
export class  ExpansionPanelModule {
}
