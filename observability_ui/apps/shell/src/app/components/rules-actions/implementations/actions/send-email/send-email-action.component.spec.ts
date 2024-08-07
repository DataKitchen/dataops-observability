import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AbstractRule } from '../../../abstract.rule';
import { SendEmailActionComponent } from './send-email-action.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { RunProcessedStatus, TaskStatusEmailTemplate } from '@observability-ui/core';

describe('send-email-action', () => {

  let component: SendEmailActionComponent;
  let fixture: ComponentFixture<SendEmailActionComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        SendEmailActionComponent,
        NoopAnimationsModule,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(SendEmailActionComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('#parse', () => {
    it('should parse recipients array', () => {
      component.parse({
        recipients: [ 'ab', 'cd', 'ef' ]
      });
      expect(component.form.controls.recipients.value).toEqual('ab, cd, ef');
    });

    it('should set template', () => {
      const template = TaskStatusEmailTemplate[RunProcessedStatus.Running];
      component.parse({
        recipients: [ 'ab', 'cd', 'ef' ],
        template,
      });
      expect(component.form.controls.template.value).toEqual(template);
    });

  });

  describe('#hydrateFromRule', () => {
    it('should set the email template from the task status rule', () => {
      component.hydrateFromRule({
        type: 'task_status',
        form: {
          value: {
            matches: RunProcessedStatus.Failed
          }
        },
      } as AbstractRule);

      expect(component.form.value.template).toEqual(TaskStatusEmailTemplate[RunProcessedStatus.Failed]);
    });

    it('should set the email template from the metric log rule', () => {
      component.hydrateFromRule({
        type: 'metric_log',
        form: {
          value: {}
        },
      } as AbstractRule);

      expect(component.form.value.template).toEqual('metric_log');
    });
  });

  describe('#toJSON', () => {
    it('should should be defensive', () => {
      expect(component.toJSON()).toEqual(expect.objectContaining({
        action_args: {recipients: []},
      }));
    });

    it('should defensive against null', () => {

      component.form.controls.recipients.setValue(null);
      expect(component.toJSON()).toEqual(expect.objectContaining({
        action_args: {recipients: []},
      }));

    });

    it('should render to action json', () => {
      component.form.patchValue({
        recipients: 'ab, cd, ef',
      });

      expect(component.toJSON()).toEqual(expect.objectContaining({
        action_args: {recipients: [ 'ab', 'cd', 'ef' ]},
      }));
    });

    it('should render the action json without a template when not set', () => {
      component.form.patchValue({
        recipients: 'ab, cd, ef',
      });

      const action = component.toJSON();
      expect(Object.keys(action.action_args)).not.toContain('template');
    });

    it('should render the action json with a template', () => {
      component.form.patchValue({
        template: 'task-status-warning',
        recipients: 'ab, cd, ef',
      });

      const action = component.toJSON();
      expect(action.action_args.template).toBe('task-status-warning');
    });
  });

});
