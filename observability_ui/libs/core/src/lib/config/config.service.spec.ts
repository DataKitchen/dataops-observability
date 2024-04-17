import { TestBed } from '@angular/core/testing';
import { ConfigService } from './config.service';
import { AppConfiguration } from './app-configuration';
import { HttpClientTestingModule } from '@angular/common/http/testing';
import spyOn = jest.spyOn;
import { TestScheduler } from '@datakitchen/rxjs-marbles';
import { of } from 'rxjs';

describe('ConfigService', () => {
  let service: ConfigService;

  const config: AppConfiguration = {
    apiBaseUrl: 'abc',
  } as AppConfiguration;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [
        HttpClientTestingModule
      ],
    });

    const storage: { [k: string]: string } = {};

    service = TestBed.inject(ConfigService);
    service.setConfig(config);

    spyOn(console, 'warn').mockImplementation();
    localStorage.setItem = jest.fn().mockImplementation((key, value) => {
      storage[key] = value;
    });
    localStorage.removeItem = jest.fn().mockImplementation(key => {
      delete storage[key];
    });
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should flag as ready$ once set', () => {
    new TestScheduler().expectObservable(service.ready$).toEqual(of(true));
  });

  describe('getApiUrl', () => {
    it('should get apiBaseUrl from app configuration', () => {
      localStorage.removeItem('apiBaseUrl');
      expect(service.get('apiBaseUrl')).toEqual('abc');
    });
  });
});
