import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TaskStatusRuleComponent } from './task-status-rule.component';
import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { MockModule } from 'ng-mocks';
import { TranslationModule } from '@observability-ui/translate';

describe('status-state-rule.component', () => {

  let component: TaskStatusRuleComponent;
  let fixture: ComponentFixture<TaskStatusRuleComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MatSelectModule,
        TaskStatusRuleComponent,
        MockModule(TranslationModule),
      ],
      declarations: [  ],
    }).compileComponents();

    fixture = TestBed.createComponent(TaskStatusRuleComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

});
