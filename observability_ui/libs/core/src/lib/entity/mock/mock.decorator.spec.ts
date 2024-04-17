import { Mock } from './mock.decorator';
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { Injectable } from '@angular/core';
import { MockProvider } from 'ng-mocks';
import { ReadOnlyRestApiService } from '../read-only-rest-api.service';
import { Entity } from '../entity.model';
import { ConfigService } from '../../config/config.service';
import spyOn = jest.spyOn;
import { EntityType } from '../entity-type';


describe('@Mock', () => {

  const mockedData = [ 'xyz' ];

  type User = Entity

  @Injectable()
  class TestClass extends ReadOnlyRestApiService<User> {

    protected readonly baseEntity = 'User' as EntityType;
    protected override readonly path: string = 'v1';
    protected override readonly prefix: string = 'prefix';

    spy = jest.fn();

    @Mock(mockedData)
    method() {
      this.spy();
      return this.http.get(this.getUrl());
    }

    @Mock((request: { parentId: string }) => {
      return [ '0', request ];
    })
    methodB(request: { parentId: string }) {
      return this.http.post(this.getUrl(request.parentId), request);
    }

  }

  let instance: TestClass;
  let httpController: HttpTestingController;

  beforeEach(() => {

    TestBed.configureTestingModule({
      imports: [ HttpClientTestingModule ],
      providers: [
        TestClass,
        // @ts-ignore
        MockProvider(ConfigService, {
          get: () => 'baseUrl'
        })
      ]
    });

    instance = TestBed.inject(TestClass);
    httpController = TestBed.inject(HttpTestingController);


    // start always with a clean sessionStorage
    global.sessionStorage.clear();

    // silencing console
    spyOn(console, 'info').mockImplementation();
  });

  it('should create', () => {
    expect(instance).toBeTruthy();
  });



  describe('return mocked data', () => {

    describe('while endpoint is not available', () => {

      describe('using a value as mock data', () => {

        it('should return mocked data', (done) => {

          instance.method().subscribe((v) => {

            expect(v).toEqual(mockedData);
            done();
          });

          httpController.expectOne('baseUrl/prefix/v1/users').error(new ProgressEvent('error'));
        });

        it('should ignore override settings through sessionStorage', (done) => {

          global.sessionStorage.setItem('baseUrl/prefix/v1/users', 'true');

          instance.method().subscribe((v) => {

            expect(v).toEqual(mockedData);
            done();
          });

          httpController.expectOne('baseUrl/prefix/v1/users').error(new ProgressEvent('error'));
        });

      });

      describe('using a value as mock data', () => {

        it('should return mocked data', (done) => {

          instance.methodB({ parentId: '1' }).subscribe((v) => {

            expect(v).toEqual([ '0', { parentId: '1' } ]);
            done();
          });

          httpController.expectOne('baseUrl/prefix/v1/users').error(new ProgressEvent('error'));
        });

        it('should ignore override settings through sessionStorage', (done) => {

          global.sessionStorage.setItem('baseUrl/prefix/v1/users', 'true');

          instance.methodB({ parentId: '1' }).subscribe((v) => {

            expect(v).toEqual([ '0', { parentId: '1' } ]);
            done();
          });

          httpController.expectOne('baseUrl/prefix/v1/users').error(new ProgressEvent('error'));
        });

      });
    });

    describe('while endpoint is available', () => {

      describe('using a variable as mock data', () => {

        it('should return mocked data', (done) => {

          instance.method().subscribe((v) => {

            expect(v).toEqual(mockedData);
            done();
          });

          httpController.expectOne('baseUrl/prefix/v1/users').flush([ 1, 'original response' ]);
        });

        it('should return original data if sessionStorageOverride is set', (done) => {
          global.sessionStorage.setItem('baseUrl/prefix/v1/users', 'true');

          instance.method().subscribe((v) => {

            expect(v).toEqual([ 1, 'original response' ]);
            done();
          });

          httpController.expectOne('baseUrl/prefix/v1/users').flush([ 1, 'original response' ]);

        });
      });

      describe('using a function as mock data', () => {

        it('should return mocked data', (done) => {

          instance.methodB({ parentId: '1' }).subscribe((v) => {

            expect(v).toEqual([ '0', { parentId: '1' } ]);
            done();
          });

          httpController.expectOne('baseUrl/prefix/v1/users').flush([ 1, 'original response' ]);
        });

        it('should return original data if sessionStorageOverride is set', (done) => {
          global.sessionStorage.setItem('baseUrl/prefix/v1/users', 'true');

          instance.methodB({ parentId: '1' }).subscribe((v) => {

            expect(v).toEqual([ 1, 'original response' ]);
            done();
          });

          httpController.expectOne('baseUrl/prefix/v1/users').flush([ 1, 'original response' ]);
        });
      });
    });
  });

});
