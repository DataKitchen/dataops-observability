import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { TestStatusRuleComponent } from './test-status-rule.component';

describe('test-status-rule.component', () => {

  let component: TestStatusRuleComponent;
  let fixture: ComponentFixture<TestStatusRuleComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MatSelectModule,
        TestStatusRuleComponent,
        MatFormFieldModule,
      ],
      declarations: [],
    }).compileComponents();

    fixture = TestBed.createComponent(TestStatusRuleComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

});
