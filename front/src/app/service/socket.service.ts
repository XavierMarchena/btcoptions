import { Injectable } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { Observer } from 'rxjs/Observer';

import * as socketIo from 'socket.io-client';
import { environment } from '../../environments/environment';


import  user_info_schema  from  './user_info_schema.json';
import  make_bet_schema  from  './make_bet_schema.json';

import Ajv from 'ajv';
//const SERVER_URL = 'http://66.248.206.91:5000';  // prod
//const SERVER_URL = 'https://socketio.rgtslots.com'; // Pruebas
//const SERVER_URL = 'http://192.168.99.100:5000'; //dev TODO:config

const ajv = new Ajv({allErrors: true});
const SERVER_URL = environment.socketUrl; //dev TODO:config

// Actions you can take on the App
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

@Injectable()
export class SocketService {
private socket;



/**
 * Initialize connection with socket server
 * @param a first input to sum
 * @param b second input to sum
 * @returns sum of a and b
 */
     public initSocket(): void {


     this.socket = socketIo(SERVER_URL, {secure: true});


    }

    /**
     * Send message to socket with range of price
     * @param a first input to sum
     * @param b second input to sum
     * @returns sum of a and b
     */

    public sendRange(message: any): void {
        var json = {};
        json['range'] = message;
        //todo:add json validation schema
        this.socket.emit('btc_range_price', json);
    }

    /**
     * Send message to socket with user information
     * @param a first input to sum
     * @param b second input to sum
     * @returns sum of a and b
     */
    public sendUserInfo(token:any, idgame:any, lang: any, currency: any, homeurl: any): void {
        var json = {};

        //json['client_id'] = client_id;
        json['token'] = token;
        json['idgame'] = idgame;
        json['lang'] = lang;
        json['currency'] = currency;
        json['homeurl'] = homeurl;
        //todo:add json validation schema

        const validate = ajv.compile(user_info_schema);


        const  valid = validate(json);
        if (!valid) console.log(validate.errors);

        this.socket.emit('user_info', json);
    }

    /**
     * Send message to socket with bet information
     * @param a first input to sum
     * @param b second input to sum
     * @returns sum of a and b
     */
    public sendBet(profit_on_win:any, bet_amount:any, type: any,superbet:any,btc_price: any, token: any, homeurl:any, round_id:any, currency:any, idgame:any): void {
        var json = {};
        var extra = {};
        json['profit_on_win'] = profit_on_win;
        json['bet_amount'] = parseFloat(bet_amount);
        extra['type'] = type; // 1 higher 0 lower;
        extra['superbet'] = superbet;
        extra['btc_price'] = btc_price;
        json['extras'] = extra;

        json['token'] = token;
        json['homeurl'] = homeurl;
        json['round_id'] = round_id;
        //json['client_id'] = client_id;
        json['currency'] = currency;
        json['idgame'] = idgame;

        //todo:add json validation schema
        const validate = ajv.compile(make_bet_schema);
        const  valid = validate(json);
        if (!valid) console.log(validate.errors);
        //console.log(json);

        this.socket.emit('make_bet', json);

    }

    /**
     * Send message to socket with bet information
     * @param a first input to sum
     * @param b second input to sum
     * @returns sum of a and b
     */
    public sendBets(token: any,  idgame:any, betHistory:any): void {
        var json = {};
        var extra = {};

        json['token'] = token;

        json['idgame'] = idgame;

        json['betHistory'] = betHistory;

        //todo:add json validation schema
       // const validate = ajv.compile(make_bet_schema);
       // const  valid = validate(json);
        //if (!valid) console.log(validate.errors);
        //console.log(json);

        this.socket.emit('bets', json);

    }


    /**
     * Takes data from UI and sends it to socket server
     * @param a first input to sum
     * @param b second input to sum
     * @returns sum of a and b
     */
    public livePrice(): void {
        //var json = {};
        //json['range'] = message;

        this.socket.emit('btc_live_price');
    }





    /**
     * //TODO: RENAME TO onLivePrice
     * @param a first input to sum
     * @param b second input to sum
     * @returns sum of a and b
     */

    public onMessage(): Observable<any> {
        return new Observable<any>(observer => {
            this.socket.on('btc_live_price', (data: any) => observer.next(data));
        });
    }

    /**
     * Takes data from UI and sends it to socket server
     * @param a first input to sum
     * @param b second input to sum
     * @returns sum of a and b
     */
    public onRange(): Observable<any> {
        return new Observable<any>(observer => {
            this.socket.on('btc_range_price', (data: any) => observer.next(data));
        });
    }

    /**
     * Takes data from UI and sends it to socket server
     * @param a first input to sum
     * @param b second input to sum
     * @returns sum of a and b
     */
    public onBets(): Observable<any> {
        return new Observable<any>(observer => {
            this.socket.on('bets', (data: any) => observer.next(data));
        });
    }


    /**
     * Takes data from UI and sends it to socket server
     * @param a first input to sum
     * @param b second input to sum
     * @returns sum of a and b
     */
    public onBetResult(): Observable<any> {
        return new Observable<any>(observer => {
            this.socket.on('make_bet', (data: any) => observer.next(data));
        });
    }

    /**
     * Takes data from UI and sends it to socket server
     * @param a first input to sum
     * @param b second input to sum
     * @returns sum of a and b
     */
    public onUserInfo(): Observable<any> {
        return new Observable<any>(observer => {
            this.socket.on('user_info', (data: any) => observer.next(data));
        });
    }

    /**
     * Takes data from UI and sends it to socket server
     * @param a first input to sum
     * @param b second input to sum
     * @returns sum of a and b
     */
    public onEvent(event: Event): Observable<any> {
        return new Observable<Event>(observer => {
            this.socket.on(event, () => observer.next());
        });
    }
}
