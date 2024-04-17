import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SummaryItemComponent } from './summary-item.component';

describe('summary', () => {
  let component: SummaryItemComponent;
  let fixture: ComponentFixture<SummaryItemComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ SummaryItemComponent, ],
    }).compileComponents();

    fixture = TestBed.createComponent(SummaryItemComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
