import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TemplatingAlertComponent } from './templating-alert.component';

describe('templating-alert', () => {
  let component: TemplatingAlertComponent;
  let fixture: ComponentFixture<TemplatingAlertComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TemplatingAlertComponent ],
    }).compileComponents();

    fixture = TestBed.createComponent(TemplatingAlertComponent);
    component = fixture.componentInstance;
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
