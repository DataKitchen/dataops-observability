import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SelectedActionsComponent } from './selected-actions.component';

describe('SelectedActionsComponent', () => {
  let fixture: ComponentFixture<SelectedActionsComponent>;
  let component: SelectedActionsComponent;

  beforeEach(async () => {
    TestBed.configureTestingModule({
      imports: [
        SelectedActionsComponent,
      ],
    });

    fixture = TestBed.createComponent(SelectedActionsComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeDefined();
  });
});
