import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TaskTestSummaryComponent } from './task-test-summary.component';
import { MockModule } from 'ng-mocks';
import { TranslationModule } from '@observability-ui/translate';

describe('task-test-summary', () => {
  let component: TaskTestSummaryComponent;
  let fixture: ComponentFixture<TaskTestSummaryComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ MockModule(TranslationModule), TaskTestSummaryComponent, ],
    }).compileComponents();

    fixture = TestBed.createComponent(TaskTestSummaryComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
