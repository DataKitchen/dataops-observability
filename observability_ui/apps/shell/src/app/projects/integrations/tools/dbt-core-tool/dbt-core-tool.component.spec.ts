import { ComponentFixture, TestBed } from '@angular/core/testing';
import { MockProvider, Mocked } from '@datakitchen/ngx-toolkit';
import { ConfigService, ProjectService } from '@observability-ui/core';
import { NoopAnimationsModule } from '@angular/platform-browser/animations';
import { DBTCoreToolComponent } from './dbt-core-tool.component';

describe('DBTCoreToolComponent', () => {
  const apiHost = 'http://test.domain.com';

  let configService: Mocked<ConfigService>;

  let component: DBTCoreToolComponent;
  let fixture: ComponentFixture<DBTCoreToolComponent>;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        NoopAnimationsModule,
        DBTCoreToolComponent,
      ],
      providers: [
        MockProvider(ConfigService),
        MockProvider(ProjectService),
      ],
    }).compileComponents();

    fixture = TestBed.createComponent(DBTCoreToolComponent);
    component = fixture.componentInstance;

    configService = TestBed.inject(ConfigService) as Mocked<ConfigService>;
    configService.get.mockReturnValue(apiHost);
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
