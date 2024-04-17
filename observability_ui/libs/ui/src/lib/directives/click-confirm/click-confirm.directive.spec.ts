import { ComponentFixture, fakeAsync, TestBed, tick } from '@angular/core/testing';
import { Component } from '@angular/core';
import { ClickConfirmDirectiveModule } from './click-confirm.directive';
import { By } from '@angular/platform-browser';
import { MatLegacySnackBarModule as MatSnackBarModule } from '@angular/material/legacy-snack-bar';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('click-confirm.directive', () => {

  @Component({
    selector: 'test-component',
    template: `
      <button (clickConfirm)="delete($event, name);"></button>
    `
  })
  class TestComponent {
    name = 'batman';
    delete = jest.fn().mockImplementation((...args) => console.log('click event', args));
  }

  let component: TestComponent;
  let fixture: ComponentFixture<TestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        ClickConfirmDirectiveModule,
        MatSnackBarModule,
        NoopAnimationsModule,
      ],
      declarations: [ TestComponent ],
    }).compileComponents();

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  describe('first click', () => {

    let button;

    beforeEach(() => {
      button = fixture.debugElement.query(By.css('button'));
      button.nativeElement.click();
    });

    it('should intercept the first click', () => {
      expect(component.delete).not.toHaveBeenCalled();
    });

  });

  describe('second click', () => {

    let button;

    beforeEach(() => {
      button = fixture.debugElement.query(By.css('button'));
      button.nativeElement.click();
      button.nativeElement.click();
    });

    it('should pass through the click event on the second click', () => {
      expect(component.delete).toHaveBeenCalled();
    });

    it('should pass through all the arguments', () => {

      expect(component.delete).toHaveBeenCalledWith(expect.anything(), component.name);

    });

  });

  describe('reset button if second click does not come within timeout', () => {

    it('should not pass through the action', fakeAsync(() => {

      const button = fixture.debugElement.query(By.css('button'));
      button.nativeElement.click();
      tick(2002);
      button.nativeElement.click();

      expect(component.delete).not.toHaveBeenCalled();
      // wait before exiting so that jest does not catch the last hanging timer
      tick(2002);
    }));

  });


});
