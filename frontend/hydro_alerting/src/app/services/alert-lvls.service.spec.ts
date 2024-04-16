import { TestBed } from '@angular/core/testing';

import { AlertLvlsService } from './alert-lvls.service';

describe('AlertLvlsService', () => {
  let service: AlertLvlsService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(AlertLvlsService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
