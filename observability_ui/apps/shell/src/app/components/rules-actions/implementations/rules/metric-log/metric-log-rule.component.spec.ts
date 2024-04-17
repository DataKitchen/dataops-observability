import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { MetricLogRuleComponent } from './metric-log-rule.component';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';

describe('metric-log-rule.component', () => {

  let component: MetricLogRuleComponent;
  let fixture: ComponentFixture<MetricLogRuleComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MatSelectModule,
        MetricLogRuleComponent,
        MatFormFieldModule,
      ],
      declarations: [  ],
    }).compileComponents();

    fixture = TestBed.createComponent(MetricLogRuleComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

});
