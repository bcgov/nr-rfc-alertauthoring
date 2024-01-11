import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BasinListComponent } from './basin-list.component';

describe('BasinListComponent', () => {
  let component: BasinListComponent;
  let fixture: ComponentFixture<BasinListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BasinListComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(BasinListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
