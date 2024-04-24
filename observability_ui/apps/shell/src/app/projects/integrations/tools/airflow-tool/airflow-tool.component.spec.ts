import { ComponentFixture, TestBed } from '@angular/core/testing';
import { AirflowToolComponent } from './airflow-tool.component';
import { MockProvider, Mocked } from '@datakitchen/ngx-toolkit';
import { ConfigService, ProjectService } from '@observability-ui/core';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';

describe('AirflowToolComponent', () => {
  const apiHost = 'http://test.domain.com';

  let configService: Mocked<ConfigService>;

  let component: AirflowToolComponent;
  let fixture: ComponentFixture<AirflowToolComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        NoopAnimationsModule,
        AirflowToolComponent,
      ],
      providers: [
        MockProvider(ConfigService),
        MockProvider(ProjectService),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(AirflowToolComponent);
    component = fixture.componentInstance;

    configService = TestBed.inject(ConfigService) as Mocked<ConfigService>;
    configService.get.mockReturnValue(apiHost);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
