import { TestBed } from '@angular/core/testing';
import { CanActivateFn } from '@angular/router';

import { editorGuard } from './editor.guard';

describe('editorGuard', () => {
  const executeGuard: CanActivateFn = (...guardParameters) => 
      TestBed.runInInjectionContext(() => editorGuard(...guardParameters));

  beforeEach(() => {
    TestBed.configureTestingModule({});
  });

  it('should be created', () => {
    expect(executeGuard).toBeTruthy();
  });
});
