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
      .subscribe((result: any) => {
        const raceResult = result[0];
        console.log(raceResult.Circuit.circuitName)
        this.raceData =  {
          circuitName: raceResult.Circuit.circuitName,
          country: raceResult?.Circuit.Location?.country,
          locality: raceResult.Circuit?.Location?.locality,
          fp1Time: raceResult.FirstPractice?.time,
          fp1Date: raceResult.FirstPractice?.date,
          fp2Time: raceResult.SecondPractice?.time,
          fp2Date: raceResult.SecondPractice?.date,
          fp3Time: raceResult.ThirdPractice?.time,
          fp3Date: raceResult.ThirdPractice?.date,
          qualiTime: raceResult.Qualifying?.time,
          qualiDate: raceResult.Qualifying?.date,
          sprintTime: raceResult.Sprint?.time,
          sprintDate: raceResult.Sprint?.date,
          date: raceResult.date,
          raceName: raceResult.raceName,
          round: +raceResult.round,
          time: raceResult.time
        };
      });
    }
  }
