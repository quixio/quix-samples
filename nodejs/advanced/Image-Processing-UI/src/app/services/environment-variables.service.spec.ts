import { TestBed } from '@angular/core/testing';

import { EnvironmentVariablesService } from './environment-variables.service';

describe('EnvironmentVariablesService', () => {
  let service: EnvironmentVariablesService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(EnvironmentVariablesService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
