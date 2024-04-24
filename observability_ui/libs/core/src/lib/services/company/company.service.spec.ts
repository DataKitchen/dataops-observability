import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import { CompanyService } from './company.service';
import { MockProvider } from 'ng-mocks';
import { ConfigService } from '../../config/config.service';

describe('company.service', () => {

  let service: CompanyService;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule
      ],
      providers: [
        CompanyService,
        MockProvider(ConfigService),
      ],
    }).compileComponents();

    service = TestBed.inject(CompanyService);
  });

  it('should create', () => {
    expect(service).toBeTruthy();
  });
});
