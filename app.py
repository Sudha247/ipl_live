import requests
from scrapy.http import HtmlResponse
import flask
from flask_cors import CORS
from flask import request
import json
from datetime import datetime

app = flask.Flask(__name__)

CORS(app)



@app.route("/", methods=["GET","POST"])

def home():

    return "Go to /scorecard?ipl_match_no=match_no to view the live scorecard of the IPL match or go to /scorecard/match_id (where match_id is the match id of cricbuzz) to view live scorecard of any other match"







@app.route('/scorecard/<match_id>')

@app.route("/scorecard", methods=["GET","POST"])

def get_entire_scorecard(match_id=None):

    '''
    Gets the entire scorecard from a match .
    Usage: /scorecard?ipl_match_no=match_no (for ipl matches) and /scorecard/match_id (Cricbuzz match Id)
    '''
    match_no = request.args.get('ipl_match_no', default = None, type = int)
    if match_no is not None:

        match_id = get_match_id_from_no(match_no)
        if match_id==-1:
            return "Invalid match no"
    else:
        match_id = match_id

    url = "https://www.cricbuzz.com/api/html/cricket-scorecard/"+str(match_id)

    cricbuzz_resp = requests.get(url)

    response = HtmlResponse(url = url,body=cricbuzz_resp.text,encoding='utf-8')

    playing_eleven = get_playing_eleven(response)
    innings_1_score, innings_2_score = get_scores(response)
    toss = get_toss(response)
    response_json = {"Innings2":
                    [{"Batsman":get_batting_scorecard('"innings_2"',response)}, {"Bowlers":get_bowling_scorecard('"innings_2"',response)},innings_2_score],
                "Innings1":
                    [{"Batsman":get_batting_scorecard('"innings_1"',response)},{"Bowlers":get_bowling_scorecard('"innings_1"',response)},innings_1_score],
                "result":get_result_update(response),
                "playing_eleven":playing_eleven,
                "toss_result" : toss
                    }

    return response_json

def get_scores(response):
    ''' scrape the innings 1 and innings 2 scores for both the teams '''

    try:
        innings_1_score = {}
        team1 = response.xpath('//*[@id="innings_1"]/div[1]/div[1]/span[1]/text()').extract()[0].replace("Innings","").strip()
        score1 = response.xpath('//*[@id="innings_1"]/div[1]/div[1]/span[2]/text()').extract()[0].replace("Innings","").strip()
        innings_1_score["team"]=team1
        innings_1_score["score"]=score1
        innings_1_score["runs"] = int(score1.split('-')[0].strip())
        innings_1_score["wickets"] = int(score1.split('-')[1].split('(')[0].strip())
        innings_1_score["overs"] = score1.split('(')[1].split(')')[0].replace('Ov','').strip()



    except:
        pass


    try:
        innings_2_score = {}
        team2 = response.xpath('//*[@id="innings_2"]/div[1]/div[1]/span[1]/text()').extract()[0].strip().replace("Innings","").strip()
        score2 = response.xpath('//*[@id="innings_2"]/div[1]/div[1]/span[2]/text()').extract()[0].strip().replace("Innings","").strip()
        innings_2_score["team"]=team2
        innings_2_score["score"]=score2
        innings_2_score["runs"] = int(score2.split('-')[0].strip())
        innings_2_score["wickets"] = int(score2.split('-')[1].split('(')[0].strip())
        innings_2_score["overs"] = score2.split('(')[1].split(')')[0].replace('Ov','').strip()
    except:
        pass

    return innings_1_score,innings_2_score



def get_playing_eleven(response):

    '''Get Playing eleven of both the teams . Only available after the toss is done '''
    try:
        
        playing_eleven = {}
        team_name_one = response.xpath(f'/html/body/div[4]/div[2]/div[9]/text()').extract()[0].replace('Squad','').strip()
        team_one_playing_eleven = response.xpath(f'/html/body/div[4]/div[2]/div[10]/div[2]/a/text()').extract()
        team_name_two = response.xpath(f'/html/body/div[4]/div[2]/div[13]/text()').extract()[0].replace('Squad','').strip()
        team_two_playing_eleven = response.xpath(f'/html/body/div[4]/div[2]/div[14]/div[2]/a/text()').extract()
        playing_eleven = {team_name_one:team_one_playing_eleven,team_name_two:team_two_playing_eleven}
    except Exception as e:
        try:
            playing_eleven = {}
            team_name_one = response.xpath(f'/html/body/div[3]/div[2]/div[9]/text()').extract()[0].replace('Squad','').strip()
            team_one_playing_eleven = response.xpath(f'/html/body/div[3]/div[2]/div[10]/div[2]/a/text()').extract()
            team_one_playing_eleven = list(map(lambda s:s.replace('(c & wk)',"").replace('(c)','').replace('(wk)','').strip(),team_one_playing_eleven))
            team_name_two = response.xpath(f'/html/body/div[3]/div[2]/div[12]/text()').extract()[0].replace('Squad','').strip()
            team_two_playing_eleven = response.xpath(f'/html/body/div[3]/div[2]/div[13]/div[2]/a/text()').extract()
            team_two_playing_eleven = list(map(lambda s:s.replace('(c & wk)',"").replace('(c)','').replace('(wk)','').strip(),team_two_playing_eleven))
            playing_eleven = {team_name_one:team_one_playing_eleven,team_name_two:team_two_playing_eleven}
            print(e)
        except Exception as e:
            print(e)
            playing_eleven = {}

    return playing_eleven

def get_toss(response):

    ''' Gets Toss Data . Available after the toss is done '''
    try:
        toss = {}
        toss_text = response.xpath('/html/body/div[4]/div[2]/div[3]/div[2]/text()').extract()[0].strip()
        toss_won_by = toss_text.split('won')[0].strip()
        chosen_to =  toss_text.split('opt to')[1].strip()
        toss["update"] = toss_text
        toss["winning_team"] = toss_won_by
        toss["chose_to"] = chosen_to

    except:
        try:
            toss = {}
            toss_text = response.xpath('/html/body/div[2]/text()').extract()[0].strip()
            toss_won_by = toss_text.split('opt to')[0].strip()
            chosen_to =  toss_text.split('opt to')[1].strip()
            toss["update"] = toss_text
            toss["winning_team"] = toss_won_by
            toss["chose_to"] = chosen_to
            pass
        except:
            toss = {}
        
    return toss

    




def get_match_id_from_no(match_no):
    ''' Returns match Ids given a match no (only valid for IPL matches)'''

    with open("./match_ids.json","r") as f:
        match_ids = json.load(f)
    for match in match_ids["IPL2021"]:
        if match['match_no']==match_no:
            return match['match_id']
    else:
        return -1


def get_result_update(response):

    ''' Get winning team and winning margin . Available after the match is completed'''

    result = response.xpath('/html/body/div[1]/text()').extract()[0].strip().lower()
    if "won" not in result:
        final_result = "Not Completed"
        margin = "NA"
    else:
        try:
            final_result = result.split('won')[0].replace('(','').replace("match tied","").strip()
            margin = result.split('by')[1].strip()
        except:
            margin = result


    return {"winning_team":final_result,"update":result,"winning_margin":margin}




@app.route('/get_all_matches')
def get_all_matches():

    ''' Returns a list of all IPL matches '''

    with open("./match_ids.json","r") as f:
        match_ids = json.load(f)
    return match_ids


@app.route('/get_all_matches_refresh')

def get_match_ids():



    match_ids = {"IPL2021":[]}
    url = "https://www.cricbuzz.com/cricket-series/3472/indian-premier-league-2021/matches"
    cricbuzz_resp = requests.get(url)
    response = HtmlResponse(url = url,body=cricbuzz_resp.text,encoding='utf-8')
        
    for i in range(3,59):
        match_time = response.xpath(f'//*[@id="series-matches"]/div[{i}]/div[3]/div[2]/div/span[2]/text()').extract()[0].strip()
        
        try:
            match_result = response.xpath(f'//*[@id="series-matches"]/div[{i}]/div[3]/div[1]/a[2]/text()').extract()[0].strip()
        except:
            match_result = "NA"
        match_id = response.xpath(f'//*[@id="series-matches"]/div[{i}]/div[3]/div[1]/a/@href').extract()[0].strip().split('cricket-scores/')[1].split('/')[0]
        match_name = response.xpath(f'//*[@id="series-matches"]/div[{i}]/div[3]/div[1]/a/span/text()').extract()[0].strip()
        match_venue = response.xpath(f'//*[@id="series-matches"]/div[{i}]/div[3]/div[1]/div/text()').extract()[0].strip()
        match_no = i-2
        match_ids["IPL2021"].append({"match_venue":match_venue,"match_result":match_result,"match_time":match_time,"match_name":match_name,"match_id":match_id,"match_no":match_no})
    print(match_ids["IPL2021"][55]["match_time"])
    date = 9
    month = 4
    for match in range(0,56):
        # print(match)
        if date>30 :
            date = 1
            month = 5
        if "03:30" in match_ids["IPL2021"][match]["match_time"]:
            match_ids["IPL2021"][match]["match_date"]=str("{0:0=2d}".format(date))+"/"+str("{0:0=2d}".format(month))+"/2021"
            continue
    
            
        else:
            match_ids["IPL2021"][match]["match_date"]=str("{0:0=2d}".format(date))+"/"+str("{0:0=2d}".format(month))+"/2021"
        date+=1

    with open("match_ids.json", "w") as outfile: 
        json.dump(match_ids, outfile)
    return match_ids








    

    




def get_batting_scorecard(innings,response):

    ''' Returns the batting scorecard of Team '''

    batting = []
    for i in range(3,13):
        try:
            batsman_name = response.xpath(f'//*[@id={innings}]/div[1]/div[{i}]/div[1]/a/text()').extract()[0].strip()
            batsman = {}
            batsman_dismissal = response.xpath(f'//*[@id={innings}]/div[1]/div[{i}]/div[2]/span/text()').extract()[0].strip()
            batsman_runs = response.xpath(f'//*[@id={innings}]/div[1]/div[{i}]/div[3]/text()').extract()[0].strip()
            batsman_balls = response.xpath(f'//*[@id={innings}]/div[1]/div[{i}]/div[4]/text()').extract()[0].strip()
            batsman_fours = response.xpath(f'//*[@id={innings}]/div[1]/div[{i}]/div[5]/text()').extract()[0].strip()
            batsman_sixes = response.xpath(f'//*[@id={innings}]/div[1]/div[{i}]/div[6]/text()').extract()[0].strip()
            batsman_sr = response.xpath(f'//*[@id={innings}]/div[1]/div[{i}]/div[7]/text()').extract()[0].strip()
            batsman["name"] = batsman_name
            batsman["dismissal"] = batsman_dismissal
            batsman["runs"] = batsman_runs
            batsman["balls"] = batsman_balls
            batsman["sixes"] = batsman_sixes
            batsman["fours"] = batsman_fours
            batsman["sr"] = batsman_sr
            batting.append(batsman)
            


            
        except Exception as e:
            pass
            
    return batting


def get_bowling_scorecard(innings,response):

    ''' Returns the bowling scorecard of Team '''

    bowling = []
    for i in range(2,13): 
        try:
            bowler_name = response.xpath(f'//*[@id={innings}]/div[4]/div[{i}]/div[1]/a/text()').extract()[0].strip()
            bowler = {}
            bowler_overs = response.xpath(f'//*[@id={innings}]/div[4]/div[{i}]/div[2]/text()').extract()[0].strip()
            bowler_maidens = response.xpath(f'//*[@id={innings}]/div[4]/div[{i}]/div[3]/text()').extract()[0].strip()
            bowler_runs = response.xpath(f'//*[@id={innings}]/div[4]/div[{i}]/div[4]/text()').extract()[0].strip()
            bowler_wicket = response.xpath(f'//*[@id={innings}]/div[4]/div[{i}]/div[5]/text()').extract()[0].strip()
            bowler_economy = response.xpath(f'//*[@id={innings}]/div[4]/div[{i}]/div[8]/text()').extract()[0].strip()
            # batsman_sr = response.xpath(f'//*[@id={innings}]/div[1]/div[{i}]/div[7]/text()').extract()[0].strip()
            bowler["name"] = bowler_name
            bowler["overs"] = bowler_overs
            bowler["maidens"] = bowler_maidens
            bowler["runs"] = bowler_runs
            bowler["wicket"] = bowler_wicket
            bowler["economy"] = bowler_economy
            bowling.append(bowler)
            
            


            
        except Exception as e:
            pass
            
    return bowling






if __name__ == "__main__":
	print("* Loading..."+"please wait until server has fully started")
	
	app.run(debug=True)