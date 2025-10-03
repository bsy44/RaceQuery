import { Component, signal } from '@angular/core';
import {Header} from './header/header';
import {RouterOutlet} from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [
    Header,
    RouterOutlet
  ],
  standalone: true,
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {}
