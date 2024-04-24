import { ComponentFixture, TestBed } from '@angular/core/testing';
import { InstanceAlertsComponent } from './instance-alerts.component';

describe('instance-alerts', () => {

  let component: InstanceAlertsComponent;
  let fixture: ComponentFixture<InstanceAlertsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ InstanceAlertsComponent ],
    }).compileComponents();

    fixture = TestBed.createComponent(InstanceAlertsComponent);
    component = fixture.componentInstance;
    component.instance = {
      id: '1',
      alerts_summary: [
        {
          count: 1,
          description: 'Something went wrong',
          level: 'ERROR'
        },
        {
          count: 2,
          description: 'Something went partially wrong',
          level: 'WARNING'
        },
        {
          count: 1,
          description: 'Something went partially wrong again',
          level: 'WARNING'
        }
      ],
    } as any;

    component.ngOnChanges({
      instance: {
        previousValue: undefined,
        currentValue: component.instance,
        firstChange: true
      } as any
    });
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should accumulate error alerts', () => {
    expect(component.errorAlerts.count).toBe(1);
  });

  it('should accumulate warning alerts', () => {
    expect(component.warningAlerts.count).toBe(3);
  });
});
