import {Component, Input, input} from '@angular/core';
import {TEAMS_INFO} from "../../teams-info";

@Component({
  selector: 'app-race-info',
  imports: [],
  templateUrl: './race-info.html',
  styleUrl: './race-info.css'
})
export class RaceInfo {
  @Input() winner!: any
  @Input() poleman!: any
  @Input() fastestLap!: any

    protected readonly TEAMS_INFO = TEAMS_INFO;
}
