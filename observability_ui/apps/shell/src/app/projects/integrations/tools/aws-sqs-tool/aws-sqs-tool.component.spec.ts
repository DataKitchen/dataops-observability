import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider, Mocked } from '@datakitchen/ngx-toolkit';
import { ConfigService, ProjectService } from '@observability-ui/core';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { AWSSQSToolComponent } from './aws-sqs-tool.component';

describe('AWSSQSToolComponent', () => {
  const apiHost = 'http://test.domain.com';

  let configService: Mocked<ConfigService>;

  let component: AWSSQSToolComponent;
  let fixture: ComponentFixture<AWSSQSToolComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        NoopAnimationsModule,
        AWSSQSToolComponent,
      ],
      providers: [
        MockProvider(ConfigService),
        MockProvider(ProjectService),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AWSSQSToolComponent);
    component = fixture.componentInstance;

    configService = TestBed.inject(ConfigService) as Mocked<ConfigService>;
    configService.get.mockReturnValue(apiHost);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
