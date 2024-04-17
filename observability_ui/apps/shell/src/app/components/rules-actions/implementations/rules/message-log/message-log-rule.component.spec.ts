import { MatLegacySelectModule as MatSelectModule } from '@angular/material/legacy-select';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatLegacyFormFieldModule as MatFormFieldModule } from '@angular/material/legacy-form-field';
import { MessageLogRuleComponent } from './message-log-rule.component';
import { FormArray, FormControl } from '@angular/forms';

describe('message-log-rule.component', () => {

  let component: MessageLogRuleComponent;
  let fixture: ComponentFixture<MessageLogRuleComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        MatSelectModule,
        MessageLogRuleComponent,
        MatFormFieldModule,
      ],
      declarations: [  ],
    }).compileComponents();

    fixture = TestBed.createComponent(MessageLogRuleComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  /*
   * tried to use a FormArray to store the values for level
   * but the code below fails.
   * Leaving it here skipped as a reminder of why we are not using a
   * FormArray
   */
  it.skip('should set values on form array', () => {
    const formArray = new FormArray<FormControl<string>>([]);
    formArray.patchValue([ 'A', 'B' ]);
    expect(formArray.value).toEqual([ 'A', 'B' ]);
  });

  describe('#toJson', () => {
    it('should set level to [] (empty array) where there are no values selected', () => {

      const data = component.toJSON();

      expect(data).toEqual(expect.objectContaining({
        rule_data: expect.objectContaining({
          conditions: [
            {
              message_log: expect.objectContaining({
                level: [],
              }),
            }
          ],
        })
      }));
    });

    it('should set levels', () => {

      component.form.patchValue({
        level: [ 'ERROR', 'INFO' ],
      });

      const data = component.toJSON();

      expect(data).toEqual(expect.objectContaining({
        rule_data: expect.objectContaining({
          conditions: [
            {
              message_log: expect.objectContaining({
                level: [ 'ERROR', 'INFO' ],
              }),
            }
          ],
        })
      }));
    });

  });


});
