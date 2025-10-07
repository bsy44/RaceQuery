import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { ActivatedRoute } from '@angular/router';
import {NgIf} from '@angular/common';

@Component({
  selector: 'app-race-details',
  templateUrl: './race-detail.html',
  imports: [NgIf],
  styleUrls: ['./race-detail.css']
})
export class RaceDetail implements OnInit {
  round!: number;
  season!: number;
  raceData: any;

  constructor(private httpClient: HttpClient, private route: ActivatedRoute) {}

  ngOnInit() {
    this.round = +this.route.snapshot.paramMap.get('round')!;
    this.season = +this.route.snapshot.paramMap.get('season')!;
    console.log()

    this.getRaceDetail();
  }

  getRaceDetail() {
  this.httpClient.get<any[]>(`http://127.0.0.1:5000/races/${this.season}/${this.round}`)
    .subscribe((result: any[]) => {
      const race = result[0];

      this.raceData = {
        circuitName: race.Circuit.circuitName,
        country: race.Circuit?.Location?.country,
        locality: race.Circuit?.Location?.locality,
        fp1Time: race.FirstPractice?.time,
        fp1Date: race.FirstPractice?.date,
        fp2Time: race.SecondPractice?.time,
        fp2Date: race.SecondPractice?.date,
        fp3Time: race.ThirdPractice?.time,
        fp3Date: race.ThirdPractice?.date,
        qualiTime: race.Qualifying?.time,
        qualiDate: race.Qualifying?.date,
        sprintTime: race.Sprint?.time,
        sprintDate: race.Sprint?.date,
        date: race.date,
        raceName: race.raceName,
        round: +race.round,
        time: race.time
      };
    });
}

}
