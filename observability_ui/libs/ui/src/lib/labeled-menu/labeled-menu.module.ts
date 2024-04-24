import { NgModule } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatMenuModule } from '@angular/material/menu';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';
import { LabeledMenuComponent } from './labeled-menu.component';


@NgModule({
  imports: [
    MatButtonModule,
    MatMenuModule,
    MatIconModule,
    CommonModule,
  ],
  exports: [
    LabeledMenuComponent,
  ],
  declarations: [
    LabeledMenuComponent,
  ],
  providers: [],
})
export class LabeledMenuModule {
}
