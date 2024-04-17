import { ComponentFixture, TestBed } from '@angular/core/testing';
import { IntegrationsPanelComponent } from './integrations-panel.component';
import { INTEGRATION_TOOLS } from '../integrations.model';
import { TranslatePipeMock } from '@observability-ui/translate';
import { MockComponents } from 'ng-mocks';
import { AlertComponent, TextFieldComponent } from '@observability-ui/ui';
import { MockComponent } from '@datakitchen/ngx-toolkit';

describe('integrations-panel', () => {

  let component: IntegrationsPanelComponent;
  let fixture: ComponentFixture<IntegrationsPanelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [
        IntegrationsPanelComponent,
        TranslatePipeMock,
        MockComponents(
          TextFieldComponent,
          AlertComponent,
        ),
        MockComponent({
          selector: 'mat-icon'
        }),
      ],
      providers: [
        {
          provide: INTEGRATION_TOOLS,
          useValue: [],
        }
      ]
    }).compileComponents();

    fixture = TestBed.createComponent(IntegrationsPanelComponent);
    component = fixture.componentInstance;

  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });



});
