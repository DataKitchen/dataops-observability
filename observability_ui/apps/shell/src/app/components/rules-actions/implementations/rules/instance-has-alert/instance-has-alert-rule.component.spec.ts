import { ComponentFixture, TestBed } from '@angular/core/testing';
import { InstanceHasAlertRuleComponent } from './instance-has-alert-rule.component';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';

describe('instance-has-alert-rule.component', () => {

  let component: InstanceHasAlertRuleComponent;
  let fixture: ComponentFixture<InstanceHasAlertRuleComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MatSelectModule,
        InstanceHasAlertRuleComponent,
      ],
      declarations: [  ],
    }).compileComponents();

    fixture = TestBed.createComponent(InstanceHasAlertRuleComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

});
