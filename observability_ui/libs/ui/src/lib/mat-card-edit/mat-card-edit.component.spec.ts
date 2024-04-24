import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MatCardEditComponent } from './mat-card-edit.component';

describe('mat-card-edit', () => {

  let component: MatCardEditComponent;
  let fixture: ComponentFixture<MatCardEditComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ MatCardEditComponent ],
    }).compileComponents();

    fixture = TestBed.createComponent(MatCardEditComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });


  it('should exit edit mode when `saving` changes from true to false ', () => {
    component.editing = true;

    fixture.componentRef.setInput('saving', true);
    fixture.detectChanges();

    fixture.componentRef.setInput('saving', false);
    fixture.detectChanges();

    expect(component.editing).toBeFalsy();

  });

  describe('toggleEdit', () => {
    it('should set editing to true if it is false', () => {
      component.editing = false;
      component.toggleEdit();

      expect(component.editing).toBeTruthy();
    });

    it('should set editing to false if it is true', () => {
      component.editing = true;
      component.toggleEdit();

      expect(component.editing).toBeFalsy();
    });
  });

  describe('onSave', () => {
    it('should emit save event', () => {
      component.save = {
        emit: jest.fn()
      } as any;

      component.onSave();
      expect(component.save.emit).toHaveBeenCalled();
    });
  });

  describe('onCancel', () => {
    it('should emit cancel event', () => {
      component.cancel = {
        emit: jest.fn()
      } as any;

      component.onCancel();
      expect(component.cancel.emit).toHaveBeenCalled();
    });
  });
});
