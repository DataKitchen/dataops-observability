import { UserService } from './user.service';
import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { ConfigService } from '../../config/config.service';

describe('user.service', () => {

  let userService: UserService;
  let httpClient: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ HttpClientTestingModule ],
      declarations: [],
      providers: [
        UserService,
        {
          provide: ConfigService,
          useClass: class {
            get = () => 'base';
          }
        },
      ]
    });

    userService = TestBed.inject(UserService);
    httpClient = TestBed.inject(HttpTestingController);
  });

  it('should exists', () => {
    expect(userService).toBeTruthy();
  });


  describe('#getUsersByCompany', () => {
    it('should return users by company', (done) => {
      userService.getUsersByCompany(123).subscribe((resp) => {
        expect(resp).toEqual({
          total: 1,
          entities: [{id: 1234}]
        });
        done();
      });

      httpClient.expectOne('base/observability/v1/companies/123/users').flush({
        total: 1,
        entities: [{id: 1234}],
        // page: 0,
        // count: 10,
      });
    });
  });
});
