import { ComponentFixture, TestBed } from '@angular/core/testing';
import { DeleteComponentDialogComponent } from './delete-component-dialog.component';
import { MockProvider } from '@datakitchen/ngx-toolkit';
import { MAT_LEGACY_DIALOG_DATA, MatLegacyDialogRef } from '@angular/material/legacy-dialog';
import { TranslatePipeMock } from '@observability-ui/translate';

describe('delete-component', () => {

  let component: DeleteComponentDialogComponent;
  let fixture: ComponentFixture<DeleteComponentDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        DeleteComponentDialogComponent,
        TranslatePipeMock,
      ],
      providers: [
        MockProvider(MatLegacyDialogRef),
        {
          provide: MAT_LEGACY_DIALOG_DATA,
          useValue: {},
        }
      ],

    }).compileComponents();

    fixture = TestBed.createComponent(DeleteComponentDialogComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

});
