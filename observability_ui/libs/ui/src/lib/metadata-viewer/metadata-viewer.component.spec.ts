import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatLegacyDialogRef as MatDialogRef, MAT_LEGACY_DIALOG_DATA as MAT_DIALOG_DATA } from '@angular/material/legacy-dialog';
import { MatIcon } from '@angular/material/icon';
import { TranslatePipeMock } from '@observability-ui/translate';
import { MockComponent, MockProvider } from 'ng-mocks';
import { NgxJsonViewerComponent } from 'ngx-json-viewer';
import { MetadataViewerComponent } from './metadata-viewer.component';
import { MatSlideToggle } from '@angular/material/slide-toggle';
import { ReactiveFormsModule } from '@angular/forms';
import { ParameterService, StorageService } from '@datakitchen/ngx-toolkit';

describe('Metadata Viewer', () => {
  const event = {
    event_type: 'MetricLogEvent',
    raw_data: {
      data: { run_key: 'A' },
      metadata: { metric: 5 }
    },
  };

  let fixture: ComponentFixture<MetadataViewerComponent>;
  let component: MetadataViewerComponent;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        ReactiveFormsModule,
      ],
      providers: [
        MockProvider(MAT_DIALOG_DATA, { event }),
        MockProvider(MatDialogRef, {}),
        MockProvider(ParameterService, {}),
        MockProvider(StorageService, {}),
      ],
      declarations: [
        MetadataViewerComponent,
        TranslatePipeMock,
        MockComponent(NgxJsonViewerComponent),
        MockComponent(MatIcon),
        MockComponent(MatSlideToggle),
      ],
    });

    fixture = TestBed.createComponent(MetadataViewerComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeDefined();
  });
});
