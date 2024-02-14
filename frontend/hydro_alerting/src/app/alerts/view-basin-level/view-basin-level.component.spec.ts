import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ViewBasinLevelComponent } from './view-basin-level.component';

describe('ViewBasinLevelComponent', () => {
  let component: ViewBasinLevelComponent;
  let fixture: ComponentFixture<ViewBasinLevelComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ViewBasinLevelComponent]
    })
    .compileComponents();
    
    fixture = TestBed.createComponent(ViewBasinLevelComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
