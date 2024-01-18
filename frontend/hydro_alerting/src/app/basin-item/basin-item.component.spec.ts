import { ComponentFixture, TestBed } from '@angular/core/testing';

import { BasinItemComponent } from './basin-item.component';

describe('BasinItemComponent', () => {
  let component: BasinItemComponent;
  let fixture: ComponentFixture<BasinItemComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [BasinItemComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(BasinItemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
