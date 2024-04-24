import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ActionTemplateComponent } from './action-template.component';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('action-template', () => {

  let component: ActionTemplateComponent;
  let fixture: ComponentFixture<ActionTemplateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        ActionTemplateComponent,
        NoopAnimationsModule,
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ActionTemplateComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

});
