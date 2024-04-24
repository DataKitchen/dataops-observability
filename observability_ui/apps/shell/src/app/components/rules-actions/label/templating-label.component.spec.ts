import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TemplatingLabelComponent } from './templating-label.component';

describe('templating-label', () => {

  let component: TemplatingLabelComponent;
  let fixture: ComponentFixture<TemplatingLabelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ TemplatingLabelComponent ],
    }).compileComponents();

    fixture = TestBed.createComponent(TemplatingLabelComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });



});
