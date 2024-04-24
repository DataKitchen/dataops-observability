import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider, Mocked } from '@datakitchen/ngx-toolkit';
import { ConfigService, ProjectService } from '@observability-ui/core';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { AzureFunctionsToolComponent } from './azure-functions-tool.component';

describe('AzureFunctionsToolComponent', () => {
  const apiHost = 'http://test.domain.com';

  let configService: Mocked<ConfigService>;

  let component: AzureFunctionsToolComponent;
  let fixture: ComponentFixture<AzureFunctionsToolComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        NoopAnimationsModule,
        AzureFunctionsToolComponent,
      ],
      providers: [
        MockProvider(ConfigService),
        MockProvider(ProjectService),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AzureFunctionsToolComponent);
    component = fixture.componentInstance;

    configService = TestBed.inject(ConfigService) as Mocked<ConfigService>;
    configService.get.mockReturnValue(apiHost);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
