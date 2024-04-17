import { ComponentFixture, TestBed } from '@angular/core/testing';
import { EmptyStateSetupComponent } from './empty-state-setup.component';

describe('EmptyStateSetupComponent', () => {
  let component: EmptyStateSetupComponent;
  let fixture: ComponentFixture<EmptyStateSetupComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ EmptyStateSetupComponent ]
    })
    .compileComponents();

    fixture = TestBed.createComponent(EmptyStateSetupComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
