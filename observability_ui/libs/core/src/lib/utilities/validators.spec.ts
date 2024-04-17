import { FormControl, ValidationErrors } from '@angular/forms';
import { Observable, of } from 'rxjs';
import { CustomValidators } from './validators';

const names = [ 'name1', 'name2', 'name3' ];
const namesAsync = of(names);

describe('CustomValidators', () => {

  describe('forbiddenNames', () => {
    const validator = CustomValidators.forbiddenNames(names);

    it('should return error, if list contains value', () => {
      const control = new FormControl(names[0]);
      expect(validator(control)).toEqual({ nameExists: expect.anything() });
    });

    it('should not return error, if list does not contain value', () => {
      const control = new FormControl('test-not-in-list');
      expect(validator(control)).toEqual(null);
    });

    it('should return null if control.value is null', () => {
      const control = new FormControl(null);
      expect(validator(control)).toEqual(null);
    });
  });

  describe('forbiddenNamesAsync', () => {
    const validator = CustomValidators.forbiddenNamesAsync(namesAsync);

    it('should return error, if list contains value', (done) => {
      const control = new FormControl(names[0]);
      const error$ = validator(control) as Observable<ValidationErrors>;

      error$.subscribe((value) => {
        expect(value).toEqual({ nameExists: expect.anything() });
        done();
      });
    });

    it('should not return error, if list does not contain value', (done) => {
      const control = new FormControl('not-in-list');
      const error$ = validator(control) as Observable<ValidationErrors>;

      error$.subscribe((value) => {
        expect(value).toEqual(null);
        done();
      });
    });


  });

  describe('emails', () => {
    const form = new FormControl('', [ CustomValidators.emails() ]);

    it('should validate empty string', () => {
      form.setValue('');
      expect(form.hasError('email')).toBeFalsy();
    });

    it('should validate a `separator` list of emails (valid emails)', () => {
      form.setValue('test@test.it, test2@test.it');
      expect(form.hasError('email')).toBeFalsy();
    });

    it('should validate a `separator` list of emails (invalid emails)', () => {
      form.setValue('test_test.it, test2@&test.it, test#@test.it, ');
      expect(form.hasError('email')).toBeTruthy();
    });

    it('should validate with a custom `separator`', () => {
      const form2 = new FormControl('', [ CustomValidators.emails(';') ]);
      form2.setValue('test@test.it; test@test2.com; ');
      expect(form2.hasError('email')).toBeFalsy();
    });

  });

  describe('oneOf', () => {
    const form = new FormControl('', [ CustomValidators.oneOf([ 'A', 'B', 'D' ]) ]);

    it('should fail for not included values', () => {
      form.setValue('C');
      expect(form.hasError('oneOf')).toBeTruthy();
    });

    it('should validate included values', () => {
      form.setValue('D');
      expect(form.hasError('oneOf')).toBeFalsy();
    });
  });
});
