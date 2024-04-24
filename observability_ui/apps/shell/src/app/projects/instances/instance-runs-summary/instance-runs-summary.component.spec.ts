import { ComponentFixture, TestBed } from '@angular/core/testing';
import { InstanceRunsSummaryComponent } from './instance-runs-summary.component';

describe('instance-runs-summary', () => {

  let component: InstanceRunsSummaryComponent;
  let fixture: ComponentFixture<InstanceRunsSummaryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ InstanceRunsSummaryComponent ],
    }).compileComponents();

    fixture = TestBed.createComponent(InstanceRunsSummaryComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });



});
