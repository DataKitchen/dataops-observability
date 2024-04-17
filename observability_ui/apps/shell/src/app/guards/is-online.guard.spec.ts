import { TestBed } from '@angular/core/testing';

import { IsOnlineGuard } from './is-online.guard';
import { RouterTestingModule } from '@angular/router/testing';
import { UrlTree } from '@angular/router';

describe('IsOnlineGuard', () => {
  let guard: IsOnlineGuard;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [ RouterTestingModule ],
    });
    guard = TestBed.inject(IsOnlineGuard);
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });

  it('should redirect to offline if client is offline', () => {

    jest.spyOn(navigator, 'onLine', 'get').mockReturnValue(false);

    expect((guard.canActivate() as UrlTree).toString()).toEqual('/offline');

  });
});
