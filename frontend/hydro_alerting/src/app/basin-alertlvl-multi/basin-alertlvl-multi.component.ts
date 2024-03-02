import { Component, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import {DcService } from '../services/basin-alertlvl.service';
import { DynBasinAlertlvlWrapperComponent } from '../dyn-basin-alertlvl-wrapper/dyn-basin-alertlvl-wrapper.component';
import {BasinAlertlvlComponent} from '../basin-alertlvl/basin-alertlvl.component';
import { DynamicComponent } from './dynamic.component';


@Component({
  selector: 'app-basin-alertlvl-multi',
  standalone: true,
  imports: [
    CommonModule,
    DynBasinAlertlvlWrapperComponent,
    BasinAlertlvlComponent,
  ],
  templateUrl: './basin-alertlvl-multi.component.html',
  styleUrl: './basin-alertlvl-multi.component.css'
})
export class BasinAlertlvlMultiComponent {
  // This component implements a button that allow for adding of multiple 
  // basin alert level components to the page.
  dynamicService = inject(DcService);
  components = this.dynamicService.getDynamicComponents();  

}
