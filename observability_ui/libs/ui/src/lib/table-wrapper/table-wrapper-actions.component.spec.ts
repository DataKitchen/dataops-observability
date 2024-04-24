import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TableWrapperActionsComponent } from './table-wrapper-actions.component';

describe('table-wrapper-actions', () => {

  let component: TableWrapperActionsComponent;
  let fixture: ComponentFixture<TableWrapperActionsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TableWrapperActionsComponent ],
    }).compileComponents();

    fixture = TestBed.createComponent(TableWrapperActionsComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
