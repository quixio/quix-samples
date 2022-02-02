import { TestBed } from '@angular/core/testing';

import { QuixService } from './quix.service';

describe('QuixService', () => {
  let service: QuixService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(QuixService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
