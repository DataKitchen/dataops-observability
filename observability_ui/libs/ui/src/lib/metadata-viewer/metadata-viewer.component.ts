import { Component, Inject, OnInit } from '@angular/core';
import { MAT_LEGACY_DIALOG_DATA as MAT_DIALOG_DATA } from '@angular/material/legacy-dialog';
import { CoreComponent, ParameterService, PersistOnLocalStorage, StorageService, TypedFormControl, TypedFormGroup } from '@datakitchen/ngx-toolkit';
import { EventType } from '@observability-ui/core';

export interface MetadataViewerData {
  title: string;
  timestamp: string;
  all: EventType | object;
  metadata?: unknown;
}

@Component({
  selector: 'shell-metadata-viewer',
  templateUrl: 'metadata-viewer.component.html',
  styleUrls: [ 'metadata-viewer.component.scss' ],
})
export class MetadataViewerComponent extends CoreComponent implements OnInit {
  event?: EventType;

  @PersistOnLocalStorage({ namespace: 'metadata-viewer' })
  form = new TypedFormGroup<{ metadataOnly: boolean }>({
    metadataOnly: new TypedFormControl<boolean>(true),
  });

  constructor(
    paramService: ParameterService,
    storageService: StorageService,
    @Inject(MAT_DIALOG_DATA) public data: MetadataViewerData,
  ) {
    super(paramService, storageService);
  }

  override ngOnInit(): void {
    super.ngOnInit();

    this.event = this.data.all as EventType;
  }
}
