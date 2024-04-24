import { CommonModule } from '@angular/common';
import { NgModule } from '@angular/core';
import { MatIconModule } from '@angular/material/icon';
import { MatLegacyDialogModule as MatDialogModule } from '@angular/material/legacy-dialog';
import { MatLegacyButtonModule as MatButtonModule } from '@angular/material/legacy-button';
import { NgxJsonViewerModule } from 'ngx-json-viewer';
import { MetadataViewerComponent } from './metadata-viewer.component';
import { TranslationModule } from '@observability-ui/translate';
import { MatLegacySlideToggleModule as MatSlideToggleModule } from '@angular/material/legacy-slide-toggle';
import { ReactiveFormsModule } from '@angular/forms';

@NgModule({
  imports: [
    CommonModule,
    MatIconModule,
    MatDialogModule,
    MatButtonModule,
    NgxJsonViewerModule,
    TranslationModule.forChild(),
    MatSlideToggleModule,
    ReactiveFormsModule
  ],
  declarations: [ MetadataViewerComponent ],
  exports: [ MetadataViewerComponent ],
})
export class MetadataViewerModule {}
