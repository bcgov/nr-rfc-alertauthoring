import { TestBed } from '@angular/core/testing';

import { BasinService } from './basin.service';

describe('BasinService', () => {
  let service: BasinService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BasinService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
