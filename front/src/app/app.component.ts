import { Component , OnInit, ViewChild} from '@angular/core';
import { SocketService } from './service/socket.service';
import { Observable } from 'rxjs';
import { HttpClient, HttpHeaders, HttpParams } from '@angular/common/http';
import { Chart } from 'chart.js';
import { trigger, state, style, animate, transition } from '@angular/animations';
import {ModalDirective} from 'angular-bootstrap-md';
import { AlertService } from './alert.service';
//import { IsLoadingService } from '@service-work/is-loading';
import {TranslateService} from '@ngx-translate/core';
import * as $ from "jquery";

export enum Action {
    JOINED,
    LEFT,
    RENAME
}

// Socket.io events
export enum Event {
    CONNECT = 'connect',
    DISCONNECT = 'disconnect'
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss','./app.component-desktop.scss','./app.component-mobile.scss'],
  providers: [SocketService],
  animations: [trigger('EnterLeave', [
  state('flyIn', style({ transform: 'translateX(0)' })),
  transition(':enter', [
    style({ transform: 'translateX(-100%)' }),
    animate('0.5s 300ms ease-in')
  ]),
  transition(':leave', [
    animate('0s ease-out', style({ transform: '' }))
  ])
])]
})

export class AppComponent implements OnInit {
@ViewChild(ModalDirective, {static: false}) modal: ModalDirective;
isLoading: Observable<boolean>;


  title = 'btcoptions';
  public chartType: string = 'line';
  action = Action;
  user: any;
  messages: any[] = [];
  messageContent: string;
  ioConnection: any;
  ioConnectionRange: any;
  ioConnectionBet: any;
  ioConnectionBets: any;
  ioConnectionUserInfo: any;
  ioGame: any;
  private client_id: any;
  private token: any;
  private idgame: any;
  public lang: any;
  public currency: any;
  private homeurl: any;
  btcValue: any = 0;
  btcBetValue: any = 0;
  public resultBtcValueMap = new Map();

  spanTie: boolean = false;
  spanWin: boolean = false;
  spanLose: boolean = false;
  betAmount: any = 0;
  betMultiplier:any=0;
  betMin:any=0;
  betMax:any=0;
  betStep:any=0;

  profitOnWin: any = 0;
  win: any = 0;
  sound: any = true;
  isCollapsed: any = false;
  autoplay: any = false;
  betType: any = -1; //todo: check if specific types
  betValue : any = 0;
  betHistory:any = 'my';

  private intervalUpdate: any = null;
  public chart: any = null;
  public arrayValue = [];
  public arrayTime = [];
  public counter : any  = 0;
  public balance : any = 0;
  public round_id: any = 1;
  public loading: boolean = false;
  bandera : boolean = false;
  min: any = 9999999;
  max: any = 0;
  typeGraph : any = 1;

  bets: any = [];
  headElementsEN = ['date', 'win', 'profit', 'result', 'bet'];
  headElementsES = ['fecha', 'ganancia', 'beneficio', 'resultado', 'apuesta'];


  constructor(private socketService: SocketService,  private alertService: AlertService, private translate: TranslateService) {

  translate.setDefaultLang('EN');


  }

  /**
   * Initialization function
   * @param a first input to sum
   * @param b second input to sum
   * @returns sum of a and b
   */
  ngOnInit(): void {
    /*Init Socket*/
    this.initIoConnection();
    this.socketService.livePrice();

    /*GET VARS FROM URL*/
    //this.client_id = this.getParamValueQueryString("client_id");
    this.token = this.getParamValueQueryString("token");
    this.idgame = this.getParamValueQueryString("idgame");
    this.lang = this.getParamValueQueryString("lang");
    this.currency = this.getParamValueQueryString("currency");
    this.homeurl = this.getParamValueQueryString("homeurl");

    this.translate.use(this.lang);

    this.socketService.sendUserInfo(this.token, this.idgame, this.lang, this.currency, this.homeurl);
    this.socketService.sendBets(this.token, this.idgame, this.betHistory);





    /*INIT CHART*/
    var i = 0;
    for (i = 0; i <= 10; i++) {
      this.chartLabels.push(i+'s');
    }


  }
  /**
   * Takes data from UI and sends it to socket server
   * @param a first input to sum
   * @param b second input to sum
   * @returns sum of a and b
   */
  asIsOrder(a, b) {

    return -1;
  }



  /**
   * Get value of parameter from URL string
   * @param paramName parameter in URL string
   * @paramValue value of parameter in URL string
   */
  public getParamValueQueryString( paramName ) {
  const url = window.location.href;
  let paramValue;
  if (url.includes('?')) {
    const httpParams = new HttpParams({ fromString: url.split('?')[1] });
    paramValue = httpParams.get(paramName);
    httpParams.delete(paramName)
  }
  return paramValue;
}


/**
 * Takes data from UI and sends it to socket server
 * @param a first input to sum
 * @param b second input to sum
 * @returns sum of a and b
 */
  public changeSound(): void{
      this.sound = !this.sound;
  }
/**
 * Takes data from UI and sends it to socket server
 * @param a first input to sum
 * @param b second input to sum
 * @returns sum of a and b
 */
  public changeAutoplay(): void{
      this.autoplay = !this.autoplay;
  }



  /**
   * Takes data from UI and sends it to socket server
   * @param value first input to sum
   * @returns void
   */
  public getRange(value): void{
      if (value >= 0){
      this.typeGraph = 2;
      this.socketService.sendRange(value);
  }else{

      this.arrayValue = [];
          this.chartLabels = [];
          var i = 0;
          for (i = 0; i <= 10; i++) {
      this.chartLabels.push(i+'s');
    }
    this.typeGraph = 1;
  }


  }

    /**
   * Takes data from UI and sends it to socket server
   * @param value first input to sum
   * @returns void
   */
  public getBets(value): void{

      this.betHistory = value;
      this.socketService.sendBets(this.token, this.idgame, this.betHistory);



  }

  public chartLabels: Array<any> = [ ];

  /**
   * Configure  socket event subscription
   * @param a first input to sum
   * @param b void
   */
  private initIoConnection(): void {

    this.socketService.initSocket();


   //TODO: RENAME TO onLivePrice
    this.ioConnection = this.socketService.onMessage()
      .subscribe((message: any) => {
        console.log("message", message);
          this.btcValue = message.price;

          if (this.typeGraph == 1){

        this.arrayValue.push(message.price);


            this.chartDatasets = [
                { data: this.arrayValue }
            ];

        if (this.arrayValue.length > 11){
           this.arrayValue.shift();
         }
   }
      });

   //Range of previous prices event
      this.ioConnectionRange = this.socketService.onRange()
      .subscribe((message: any) => {
          console.log("message", message);
          this.arrayValue = [];
          this.chartLabels = [];
            for (var i = 0; i < message['range'].length; i++) {
                this.arrayValue.push(message['range'][i].price);
                var dt1 = new Date(message['range'][i].date);
                var hh = ("0" + dt1.getHours()).slice(-2);
                var mm = ("0" + dt1.getMinutes()).slice(-2);

                this.chartLabels.push(hh+":"+mm);
            }
            this.chartDatasets = [
                { data: this.arrayValue }
            ];



            /*this.chartLabels = [
                { data: [this.arrayValue], label: 'BTC Value' },

              ];   */
      });

   //Range of previous prices event
      this.ioConnectionRange = this.socketService.onBets()
      .subscribe((message: any) => {
          console.log("message", message);
          this.bets = message["bets"];


              });
//          this.arrayValue = [];
//         this.chartLabels = [];
//            for (var i = 0; i < message['range'].length; i++) {
//                this.arrayValue.push(message['range'][i].price);
//                var dt1 = new Date(message['range'][i].date);
//                var hh = ("0" + dt1.getHours()).slice(-2);
//                var mm = ("0" + dt1.getMinutes()).slice(-2);

//                this.chartLabels.push(hh+":"+mm);
//            }
//            this.chartDatasets = [
 //               { data: this.arrayValue }
  //          ];



            /*this.chartLabels = [
                { data: [this.arrayValue], label: 'BTC Value' },

              ];   */



   //Bet event
      this.ioConnectionBet = this.socketService.onBetResult()
      .subscribe((message: any) => {
        class Category {
         result: string;
         cssclass: string;
        }

        let category: Category = new Category();

          console.log("message", message);
          if(message["error"]!=200 && message["error"]!=undefined){
          this.alertService.error(message["message"]);
          this.loading = false;
          }

          if (message["counter"]!=undefined){
            this.counter = message["counter"];
          }


          if (message["balance"]){
            this.balance = message["balance"];

          }

          if (message["price_result"]){

            if (message["result"] == "win") {
              category.result = message["price_result"];
              category.cssclass = "spanWin";
              this.resultBtcValueMap.set(new Date(), category)

            }
            else if (message["result"] == "tie") {
              category.result = message["price_result"];
              category.cssclass = "spanTie";
              this.resultBtcValueMap.set(new Date(), category)

            }
            else if(message["result"] == "lose")  {
              category.result = message["price_result"];
              category.cssclass = "spanLose";
              this.resultBtcValueMap.set(new Date(), category)
            }
            this.loading = false;
            this.socketService.sendBets(this.token, this.idgame, this.betHistory);
            if (this.autoplay){
            this.bet();
            }
          }

      });

   //User info event
      this.ioConnectionUserInfo = this.socketService.onUserInfo()
      .subscribe((message: any) => {
          console.log("message", message);

          if(message["error"]!=200 && message["error"]!=undefined){

          this.alertService.error(message["message"]);

          } else {


          this.balance = message["balance"];
          this.betMultiplier = message["bet_multiplier"];

          if (this.currency =="MBTC") {
          //this.betMin = message["bet_min"];
          //this.betMax = message["bet_max"];
          //this.betStep = this.betMin;

          this.betMin = (message["bet_min"] / this.btcValue*1000).toFixed(4) ;
          this.betMax = (message["bet_max"] / this.btcValue*1000).toFixed(4) ;
          this.betStep = this.betMin;

          } else {
          //USD DEFAULT
          this.betMin =   parseFloat(message["bet_min"]).toFixed(1);
          this.betMax = parseFloat(message["bet_max"]).toFixed(1);
          this.betStep = this.betMin;
          }

          //this.betStep = (this.betMin/10).toFixed(6);
          //SET amount as min
          this.betAmount = this.betMin;

          //Trigger modelChanged to update profitOnWin
          this.modelChanged(this.betAmount);
          //this.profitOnWin = (this.betAmount * 1.5).toFixed(3);

          }


      });

    this.socketService.onEvent(Event.CONNECT)
      .subscribe(() => {
        console.log('connected');
      });

    this.socketService.onEvent(Event.DISCONNECT)
      .subscribe(() => {
        console.log('disconnected');
      });
  }



  /**
   * Sets bet type "higher"-"lower"
   *
   * @param value From html 1 higher 0 lower
   * @returns void
   */
  type(value){
          this.betType = value;
  }

  modelChanged($event) {
  console.log($event)
  if (this.currency =="MBTC") {
   this.profitOnWin = (this.betAmount * this.betMultiplier).toFixed(4);
 this.betAmount = parseFloat($event).toFixed(4);
 this.win =(this.profitOnWin - this.betAmount).toFixed(4);
  } else {
   this.profitOnWin = (this.betAmount * this.betMultiplier).toFixed(1);
 this.betAmount = parseFloat($event).toFixed(1);
  this.win =(this.profitOnWin - this.betAmount).toFixed(1);
  }


}

  handleMinus() {


      if (this.currency =="MBTC") {
        if ((parseFloat(this.betAmount)-parseFloat(this.betStep)>0)){
    this.betAmount = parseFloat((parseFloat(this.betAmount)-parseFloat(this.betStep)).toFixed(4));
       this.profitOnWin = (this.betAmount * this.betMultiplier).toFixed(4);
   this.win =(this.profitOnWin - this.betAmount).toFixed(4);

    }


 //this.betAmount = parseFloat($event);
  } else {
    if ((parseFloat(this.betAmount)-parseFloat(this.betStep)>0)){
    this.betAmount = parseFloat((parseFloat(this.betAmount)-parseFloat(this.betStep)).toFixed(1));
   this.profitOnWin = (this.betAmount * this.betMultiplier).toFixed(1);
   this.win =(this.profitOnWin - this.betAmount).toFixed(1);
 //this.betAmount = parseFloat($event);
    }

  }
  }
  handlePlus(num) {

  if (num==1){
//num condition


        if (this.currency =="MBTC") {
                  if (parseFloat((parseFloat(this.betAmount) + parseFloat(this.betStep)).toFixed(4))<=parseFloat(this.betMax)){
          //betMax condition
//currency condition
   this.betAmount = parseFloat((parseFloat(this.betAmount) + parseFloat(this.betStep)).toFixed(4));
   this.profitOnWin = (this.betAmount * this.betMultiplier).toFixed(4);
   this.win =(this.profitOnWin - this.betAmount).toFixed(4);
}
  } else { //USD
   if (parseFloat((parseFloat(this.betAmount) + parseFloat(this.betStep)).toFixed(1))<=parseFloat(this.betMax)){

      this.betAmount = parseFloat((parseFloat(this.betAmount) + parseFloat(this.betStep)).toFixed(1));
   this.profitOnWin = (this.betAmount * this.betMultiplier).toFixed(1);
   this.win =(this.profitOnWin - this.betAmount).toFixed(1);
  }
  }
  } else if (num==2) {
//num condition


          if (this.currency =="MBTC") {
      //currency condition
          if (parseFloat((parseFloat(this.betAmount) * 2.0).toFixed(4))<=parseFloat(this.betMax)){
          //betMax condition

   this.betAmount = parseFloat((parseFloat(this.betAmount) * 2.0).toFixed(4));
   this.profitOnWin = (this.betAmount * this.betMultiplier).toFixed(4);
   this.win =(this.profitOnWin - this.betAmount).toFixed(4);
}
  } else { //USD
       if (parseFloat((parseFloat(this.betAmount) * 2.0).toFixed(1))<=parseFloat(this.betMax)){
       //betMax condition


      this.betAmount = parseFloat((parseFloat(this.betAmount)  * 2.0).toFixed(1));
   this.profitOnWin = (this.betAmount * this.betMultiplier).toFixed(1);
   this.win =(this.profitOnWin - this.betAmount).toFixed(1);
  }
  }

  } else if (num==10) {
//num condition


          if (this.currency =="MBTC") {
      //currency condition
          if (parseFloat((parseFloat(this.betAmount) * 10.0).toFixed(4))<=parseFloat(this.betMax)){
          //betMax condition

   this.betAmount = parseFloat((parseFloat(this.betAmount) * 10.0).toFixed(4));
   this.profitOnWin = (this.betAmount * this.betMultiplier).toFixed(4);
   this.win =(this.profitOnWin - this.betAmount).toFixed(4);
}
  } else {
            if (parseFloat((parseFloat(this.betAmount) * 10.0).toFixed(1))<=parseFloat(this.betMax)){
          //betMax condition

      this.betAmount = parseFloat((parseFloat(this.betAmount)  * 10.0).toFixed(1));
   this.profitOnWin = (this.betAmount * this.betMultiplier).toFixed(1);
   this.win =(this.profitOnWin - this.betAmount).toFixed(1);
  }
  }
  }



  }

  /**
   * Sends vars from UI to socket server
   * @param a first input to sum
   * @param b second input to sum
   * @returns sum of a and b
   */
  bet(){
    this.loading = true;
    //this.alertService.error("Not enough balance"); //todo get from socket event
    //var audio = new Audio();
    //audio.src = "./assets/countdown.mp3";
    //audio.load();
    //audio.play();

    console.log(this.betAmount)


    this.socketService.sendBet(this.profitOnWin, this.betAmount, this.betType,0,this.btcValue, this.token, this.homeurl, this.round_id, this.currency, this.idgame);

    this.btcBetValue = this.btcValue
    this.round_id++;

  }


  /**
   * Configure chart
   * @param a first input to sum
   * @param b second input to sum
   * @returns sum of a and b
   */
  public chartDatasets: Array<any> = [
    { data: [this.arrayValue], label: 'BTC Value' },

  ];

  /**
   * Configure chart
   * @param a first input to sum
   * @param b second input to sum
   * @returns sum of a and b
   */
  setLevels(data){
       if (this.min > data.price)
            this.min = data.price;
        if (this.max > data.price)
            this.max = data.price;
  }


  /**
   * Configure chart
   * @param a first input to sum
   * @param b second input to sum
   * @returns sum of a and b
   */
  public chartColors: Array<any> = [
    {
      responsive:true,
      backgroundColor: 'rgba(34,38,74,1)',
      borderColor: 'rgba(79,92,146,1)',
      pointBackgroundColor: '#A6CEE3',
      pointBorderColor: '#A6CEE3',
      borderWidth: 2
    },
  ];

  /**
   * Configure chart
   * @param a first input to sum
   * @param b second input to sum
   * @returns sum of a and b
   */
  public chartOptions: any = { responsive: true, tooltips: { mode: 'index', intersect: false }, showAllTooltips:true };

  /**
   * Configure chart
   * @param a first input to sum
   * @param b second input to sum
   * @returns sum of a and b
   */
  public chartClicked(e: any): void { }

  /**
   * Configure chart
   * @param a first input to sum
   * @param b second input to sum
   * @returns sum of a and b
   */
  public chartHovered(e: any): void { }


  /**
   * Configure chart
   * @param a first input to sum
   * @param b second input to sum
   * @returns sum of a and b
   */

  verify(){ //TODO:REMOVE
      this.bandera = true;


      var color;
      if (this.betValue >= this.btcValue){
          if (this.betType == 0)
              color = "#2bab40";
          else
              color = "#db4931";
      }else{
          if (this.betType == 1)
              color = "#2bab40";
          else
              color = "#db4931";
      }
      var thath = this;


        setTimeout(function() {
  thath.chartColors = [
            { backgroundColor: 'rgba(105, 0, 132, .2)',
              borderColor: color,
              borderWidth: 2, }
        ];

}, 500);
        setTimeout(function() {
  thath.chartColors = [
            { backgroundColor: 'rgba(105, 0, 132, .2)',
              borderColor: 'rgba(200, 99, 132, .7)',
              borderWidth: 2, }
                ];

}, 4000);

  }



}

