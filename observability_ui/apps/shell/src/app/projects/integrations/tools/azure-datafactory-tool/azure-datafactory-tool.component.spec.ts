import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider, Mocked } from '@datakitchen/ngx-toolkit';
import { ConfigService, ProjectService } from '@observability-ui/core';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { AzureDataFactoryToolComponent } from './azure-datafactory-tool.component';

describe('AzureDataFactoryToolComponent', () => {
  const apiHost = 'http://test.domain.com';

  let configService: Mocked<ConfigService>;

  let component: AzureDataFactoryToolComponent;
  let fixture: ComponentFixture<AzureDataFactoryToolComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        NoopAnimationsModule,
        AzureDataFactoryToolComponent,
      ],
      providers: [
        MockProvider(ConfigService),
        MockProvider(ProjectService),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AzureDataFactoryToolComponent);
    component = fixture.componentInstance;

    configService = TestBed.inject(ConfigService) as Mocked<ConfigService>;
    configService.get.mockReturnValue(apiHost);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
