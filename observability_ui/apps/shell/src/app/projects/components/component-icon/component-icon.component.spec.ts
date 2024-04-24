import { ComponentFixture, TestBed } from '@angular/core/testing';
import { ComponentIconComponent } from './component-icon.component';
import { INTEGRATION_TOOLS } from '../../integrations/integrations.model';

describe('component-icon', () => {

  let component: ComponentIconComponent;
  let fixture: ComponentFixture<ComponentIconComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ ComponentIconComponent ],
      providers: [
        {
          provide: INTEGRATION_TOOLS,
          useValue: [],
        }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(ComponentIconComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

});
