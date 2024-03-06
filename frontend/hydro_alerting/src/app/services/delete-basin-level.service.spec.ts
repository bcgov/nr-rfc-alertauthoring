import { TestBed } from '@angular/core/testing';

import { DeleteBasinLevelService } from './delete-basin-level.service';

describe('DeleteBasinLevelService', () => {
  let service: DeleteBasinLevelService;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(DeleteBasinLevelService);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
