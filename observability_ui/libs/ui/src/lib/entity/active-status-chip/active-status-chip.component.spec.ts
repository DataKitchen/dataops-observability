import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActiveStatusChipComponent } from './active-status-chip.component';
import { TranslatePipeMock } from '@observability-ui/translate';

describe('Active Status Chip Component', () => {

  let fixture: ComponentFixture<ActiveStatusChipComponent>;
  let component: ActiveStatusChipComponent;

  beforeEach(() => {
    TestBed.configureTestingModule({
      declarations: [
        ActiveStatusChipComponent,
        TranslatePipeMock,
      ],
    });

    fixture = TestBed.createComponent(ActiveStatusChipComponent);
    component = fixture.componentInstance;
  });

  it('should exist', () => {
    expect(component).toBeDefined();
  });

  it('should display Active chip, if active if true', () => {
    component.active = true;
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('active');
  });

  it('should display Inactive chip, if active if not true', () => {
    component.active = false;
    fixture.detectChanges();
    expect(fixture.nativeElement.textContent).toContain('inactive');
  });
});
