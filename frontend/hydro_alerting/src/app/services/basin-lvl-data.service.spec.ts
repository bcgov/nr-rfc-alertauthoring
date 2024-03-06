import { TestBed } from '@angular/core/testing';

import { BasinLvlDataService } from './basin-lvl-data.service';

describe('BasinLvlDataService', () => {
  let service: BasinLvlDataService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(BasinLvlDataService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
