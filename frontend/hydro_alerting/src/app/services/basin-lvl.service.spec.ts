import { TestBed } from '@angular/core/testing';

import { BasinLvlService } from './basin-lvl.service';

describe('BasinLvlService', () => {
  let service: BasinLvlService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BasinLvlService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
