import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockModule } from 'ng-mocks';
import { MatIconModule } from '@angular/material/icon';
import { AlertComponent } from './alert.component';
describe('CreatedByComponent', () => {
  let fixture: ComponentFixture<AlertComponent>;
  let component: AlertComponent;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ MockModule(MatIconModule) ],
    });

    fixture = TestBed.createComponent(AlertComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
