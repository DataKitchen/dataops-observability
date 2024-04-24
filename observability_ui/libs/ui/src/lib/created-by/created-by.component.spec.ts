import { ComponentFixture, TestBed } from '@angular/core/testing';
import { CreatedByComponent } from './created-by.component';

describe('CreatedByComponent', () => {
  const createdBy = {id: '1', name: 'John Doe'};
  const createdOn = '2022-06-22T17:46:14.097997+00:00';

  let fixture: ComponentFixture<CreatedByComponent>;
  let component: CreatedByComponent;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ CreatedByComponent ],
    });

    fixture = TestBed.createComponent(CreatedByComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    component.createdBy = createdBy;
    component.createdOn = createdOn;

    expect(component).toBeTruthy();
  });
});
