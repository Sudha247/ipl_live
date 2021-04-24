import requests
from scrapy.http import HtmlResponse
import flask
from flask import request
import json

app = flask.Flask(__name__)
@app.route("/", methods=["GET","POST"])
def home():
    return "Go to /scorecard?match_no=match_no to view the live scorecard of the match"

@app.route("/scorecard", methods=["GET","POST"])

def get_entire_scorecard():
    match_no = request.args.get('match_no', default = 1, type = int)

    match_id = get_match_id_from_no(match_no)
    if match_id==-1:
        return "Invalid match no"

    url = "https://www.cricbuzz.com/api/html/cricket-scorecard/"+str(match_id)
    cricbuzz_resp = requests.get(url)
    response = HtmlResponse(url = url,body=cricbuzz_resp.text,encoding='utf-8')
    response_json = {"Innings2":
                    [{"Batsman":get_batting_scorecard('"innings_2"',response)}, {"Bowlers":get_bowling_scorecard('"innings_2"',response)}],
                "Innings1":
                    [{"Batsman":get_batting_scorecard('"innings_1"',response)},{"Bowlers":get_bowling_scorecard('"innings_1"',response)}],
                "result":get_result_update(response)
                    }

    return response_json

def get_match_id_from_no(match_no):

    with open("./match_ids.json","r") as f:
        match_ids = json.load(f)
    for match in match_ids["IPL2021"]:
        if match['match_no']==match_no:
            return match['match_id']
    else:
        return -1

# with open('resp.html') as f:
#     f.write(response.text)
def get_result_update(response):

    result = response.xpath('/html/body/div[1]/text()').extract()[0].strip()
    if "won" not in result:
        final_result = "Not Completed"
        margin = "NA"
    else:
        final_result = result.split('won')[0].strip()
        margin = result.split('by')[1].strip()


    return {"winning_team":final_result,"update":result,"winning_margin":margin}

def get_match_ids():

    match_ids = {"IPL2021":[]}
    url = "https://www.cricbuzz.com/cricket-series/3472/indian-premier-league-2021/matches"
    cricbuzz_resp = requests.get(url)
    response = HtmlResponse(url = url,body=cricbuzz_resp.text,encoding='utf-8')
    for i in range(3,59):
        match_id = response.xpath(f'//*[@id="series-matches"]/div[{i}]/div[3]/div[1]/a/@href').extract()[0].strip().split('cricket-scores/')[1].split('/')[0]
        match_name = response.xpath(f'//*[@id="series-matches"]/div[{i}]/div[3]/div[1]/a/span/text()').extract()[0].strip()
        match_no = i-2
        match_ids["IPL2021"].append({"match_name":match_name,"match_id":match_id,"match_no":match_no})

    with open("match_ids.json", "w") as outfile: 
        json.dump(match_ids, outfile)

    # return match_ids




def get_batting_scorecard(innings,response):

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



# print(get_batting_scorecard('"innings_1"'))
# print("================================================")
# print(get_batting_scorecard('"innings_2"'))
# print("================================================")

# print(get_bowling_scorecard('"innings_1"'))
# print("================================================")

# print(get_bowling_scorecard('"innings_2"'))
# print("===============")
# print(get_result_update())


# response_json = {"Innings2":
#                     [{"Batsman":get_batting_scorecard('"innings_2"')}, {"Bowlers":get_bowling_scorecard('"innings_2"')}],
#                 "Innings1":
#                     [{"Batsman":get_batting_scorecard('"innings_1"')},{"Bowlers":get_bowling_scorecard('"innings_1"')}],
#                 "result":get_result_update()
#                     }


# get_match_ids()


if __name__ == "__main__":
	print("* Loading..."+"please wait until server has fully started")
	
	app.run()