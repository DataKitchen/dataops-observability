import {ToolSelectorComponent} from "./tool-selector.component";
import {ComponentFixture, TestBed} from '@angular/core/testing';
import { INTEGRATION_TOOLS } from '../integrations.model';

describe('tool-selector', () => {

  let component: ToolSelectorComponent;
  let fixture: ComponentFixture<ToolSelectorComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ ToolSelectorComponent ],
      providers: [
        {
          provide: INTEGRATION_TOOLS,
          useValue: [],
        }
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(ToolSelectorComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

});
