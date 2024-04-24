import { NgModule } from '@angular/core';
import { AppVersionComponent } from './app-version.component';
import { CommonModule } from '@angular/common';
import { MatBottomSheetModule } from '@angular/material/bottom-sheet';
import { HttpClientModule } from '@angular/common/http';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';

@NgModule({
  imports: [
    HttpClientModule,
    CommonModule,
    MatBottomSheetModule,
    MatButtonModule
  ],
  exports: [
    AppVersionComponent
  ],
  declarations: [
    AppVersionComponent,
  ],
  providers: [

  ]
})
export class AppVersionModule {}
