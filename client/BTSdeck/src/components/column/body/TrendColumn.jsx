import React, { Component } from 'react'
import '../../../App.css';

import {IoIosSunny} from "react-icons/io"
import Header from '../header/Header'

import InfiniteScroll from 'react-infinite-scroll-component'

import cookie from 'react-cookies';
import axios from 'axios'; 

import Tweet from '../../tweets/Tweet'

const ip = "20.41.86.4:5000";
// 해시 태그 순위
// const ip = "20.41.86.218:3888";

const tweetRank = 'trend/tweet'

const trendTweetTime = "2020/02/25/17/02"
// const trendTweetTime = "tweetRank"
// const trendTime = "tweetRank"

class TrendColumn extends Component {
    state = {
        data: [],
        items: 40,
        hasMore: true
      };

    componentDidMount(){
    // ?? 
    this._getTrend();
        this.interval = setInterval(() => {
            this.setState({
                data: []
            })
            this._getTrend();
        }, 10000);
    }
    componentWillMount(){
        clearInterval(this.interval);
    }

    _getTrend(){
        let myHeaders = new Headers();

        var today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth()+1; //January is 0!
        var yyyy = today.getFullYear();
        var hour = today.getHours();
        var min = today.getMinutes() - 10;
        if(dd<10) {
            dd='0'+dd
        } 
        if(mm<10) {
            mm='0'+mm
        }
        // const trendTweetTime = "2020/02/25/17/02"

        // var td = yyyy+'/'+mm+'/'+dd;
        
        // myHeaders.append("Content-Type", "application/x-www-form-urlencoded");
        // myHeaders.append("Authorization", "Bearer " + cookie.load('access-token'));
        // console.log('쿠키 : ', cookie.load('access-token'))

        // let urlencoded = new URLSearchParams();
        // // urlencoded.append("time", `${td}/${(today.getTime())*1000}`)
        // // let trendTweetTime = `${td}/${hour}/${min}`;
        // // console.log("시간시간시간:::::::\n\n", trendTweetTime)
        // urlencoded.append("time", trendTweetTime);

        // let requestOptions = {
        //     method: 'POST',
        //     // method: 'GET',
        //     headers: myHeaders,
        //     body: urlencoded,
        //     redirect: 'follow'
        // };
    
        // fetch(`http://${ip}/${tweetRank}`,requestOptions)
        // .then(response => response.text())
        // .then(result => {
        //     var datas = JSON.parse(JSON.parse(result).message);
        //     console.log('예은데이터 : \n ',datas)

        //     datas.map((dat, index) => {
        //         this.setState({
        //                 data: datas.concat(dat)
        //             })
        //         })
        // })
        // .catch(error => console.log('error', error));


        // var myHeaders = new Headers();

        // console.log('axios 전')
        // axios.get(`http://${ip}/${tweetRank}`, {
        //     headers: {
        //         "Authorization" : "Bearer " + cookie.load('access-token')
        //       }
        // }).then(res => 
        //     res.text()
        //     // JSON.stringify(res)
        //     // console.log("석옥ㅇ송ㄱㅇ : " , res);
        // ).then(result => {
        //     console.log('result : \n ', result)
        //     var datas = JSON.parse(JSON.parse(result).message);

        //     // var datas = JSON.parse(JSON.parse(result.data).message);
        //     // var datas = JSON.parse((result.data.message))
        //     console.log('예은데이터 : \n ',datas)

        //     datas.map((dat, index) => {
        //         this.setState({
        //                 data: datas.concat(dat)
        //             })
        //         })
        // })
        // .catch(error => console.log('error', error));

        axios.get(`http://${ip}/${tweetRank}`,{
            headers: {
                "Authorization" : "Bearer " + cookie.load('access-token')
            }
        })
        .then(result => {
            console.log('asdfasdfadfsadfadfasdfsadfsafadf\n',result)
            // let datas = result.data.message
            let datas = JSON.parse(result.data.message)
            console.log("datadatassssssssssssssssss " + typeof(datas));
            // let parsedData = JSON.parse(datas)
            // console.log("datas : \n", datas)
            // var datas = JSON.parse(JSON.parse(result).message)


            
            datas.map((dat,index) => {
                console.log("ddddaaaaaaaaaatttttttTT:" + JSON.parse(dat));
                // this.setState(prevState => ({
                //     data: [... prevState.data, dat]
                // }))
                // this.setState({
                //     data: datas.concat(dat)
                // })
            })
        })
        .catch(error => console.log('error', error))
    }

    render() {
        const ee = this.state.data.map(
            (dat, index) => {
              var user = JSON.parse(dat);
              return <div>
                  <Tweet rcvData={user} />
                </div>
            });
        return (
        <div className="content">
            <div className="column-header">
                <IoIosSunny size="30" color="#38444d"/>
                <Header name="Tweet-Ranking"/>
            </div>
         <InfiniteScroll
          dataLength={this.state.data.length}
          hasMore={this.state.hasMore} // boolean 형식
          height={950}
        //   loader={<h4>Loading...</h4>}
          > 
          {ee}          
        </InfiniteScroll>
          </div>
        )
    }
}
export default TrendColumn;