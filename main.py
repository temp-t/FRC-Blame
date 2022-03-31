import requests
import json

import plotly.graph_objects as go

import numpy as np
import matplotlib.pyplot as plt

#######################################################################################
# DON'T EDIT ANYTHING OTHER THAN THESE VARIABLES IF YOU DON'T KNOW WHAT YOU ARE DOING
api_key = ''
event_key = ''
output_match_data = False
#######################################################################################

if api_key == '':
    print('No API key entered!')
    exit(2549)
if event_key == '':
    print('No event key entered!')
    exit(2550)

headers = {'X-TBA-Auth-Key': api_key}

print('Getting Matches...')

url = 'https://www.thebluealliance.com/api/v3/event/' + event_key + '/matches'
raw_matches = json.loads(requests.get(url, headers=headers).text)
match_keys = []
input_matches = {}

for match in raw_matches:
    match_keys.append(match['key'])

count = 0
for key in match_keys:
    count += 1
    url = 'https://www.thebluealliance.com/api/v3/match/' + key
    raw_match = json.loads(requests.get(url, headers=headers).text)
    input_matches[key] = raw_match

def get_alliance_cargo_penalty_points(key, alliance):
    opposing_alliance = ''
    if alliance == 'red':   
        opposing_alliance = 'blue'
    elif alliance == 'blue':
        opposing_alliance = 'red'
    scores = []
    match = input_matches[key]
    scores.append((match['score_breakdown'][alliance]['teleopCargoUpperBlue'] +
            match['score_breakdown'][alliance]['teleopCargoUpperRed'] +
            match['score_breakdown'][alliance]['teleopCargoUpperNear'] +
            match['score_breakdown'][alliance]['teleopCargoUpperFar']) * 2)
    scores.append((match['score_breakdown'][alliance]['teleopCargoLowerBlue'] +
            match['score_breakdown'][alliance]['teleopCargoLowerRed'] +
            match['score_breakdown'][alliance]['teleopCargoLowerNear'] +
            match['score_breakdown'][alliance]['teleopCargoLowerFar']))
    scores.append((match['score_breakdown'][alliance]['autoCargoUpperBlue'] +
            match['score_breakdown'][alliance]['autoCargoUpperRed'] +
            match['score_breakdown'][alliance]['autoCargoUpperNear'] +
            match['score_breakdown'][alliance]['autoCargoUpperFar']) * 4)
    scores.append((match['score_breakdown'][alliance]['autoCargoLowerBlue'] +
            match['score_breakdown'][alliance]['autoCargoLowerRed'] +
            match['score_breakdown'][alliance]['autoCargoLowerNear'] +
            match['score_breakdown'][alliance]['autoCargoLowerFar']) * 2)
    scores.append(match['score_breakdown'][opposing_alliance]['foulPoints'])
    return scores


def did_robot_taxi(key, alliance, position):
    match = input_matches[key]
    if match['score_breakdown'][alliance]['taxiRobot' + str(position)] == 'Yes':
        return 2
    elif match['score_breakdown'][alliance]['taxiRobot' + str(position)] == 'No':
        return 0
    else:
        print('Taxi API Data Error, stay calm')


def did_robot_climb(key, alliance, position):
    match = input_matches[key]
    if match['score_breakdown'][alliance]['endgameRobot' + str(position)] == 'Traversal':
        return 15
    elif match['score_breakdown'][alliance]['endgameRobot' + str(position)] == 'High':
        return 10
    elif match['score_breakdown'][alliance]['endgameRobot' + str(position)] == 'Mid':
        return 6
    elif match['score_breakdown'][alliance]['endgameRobot' + str(position)] == 'Low':
        return 4
    elif match['score_breakdown'][alliance]['endgameRobot' + str(position)] == 'None':
        return 0
    else:
        print('Climb API Data Error, stay calm')


def list_avg(list):
    sum = 0
    count = 0
    for i in range(0, len(list)):
        sum += list[i]
        count += 1
    return sum / count


def sort_dic(dic):
    return dict(sorted(dic.items(), key=lambda kv: kv[1], reverse=True))


r = requests.get('https://www.thebluealliance.com/api/v3/event/' + event_key + '/teams/keys', headers=headers)
teams = json.loads(r.text)

r = requests.get('https://www.thebluealliance.com/api/v3/event/' + event_key + '/matches/simple', headers=headers)
matches = json.loads(r.text)

team_teleop_high_scores = {}
team_teleop_low_scores = {}
team_auto_high_scores = {}
team_auto_low_scores = {}
team_penalty_points = {}
avg_teleop_high_scores = 0
avg_teleop_low_scores = 0
avg_auto_high_scores = 0
avg_auto_low_scores = 0
avg_penalty_points = 0

print('Processing Overall Team Data...')

for i in teams:
    telehighscores = []
    telelowscores = []
    autohighscores = []
    autolowscores = []
    pen_points = []
    for m in matches:
        if '_qm' in m['key']:
            if i in m['alliances']['blue']['team_keys']:
                scores = get_alliance_cargo_penalty_points(m['key'], 'blue')
                telehighscores.append(scores[0])
                telelowscores.append(scores[1])
                autohighscores.append(scores[2])
                autolowscores.append(scores[3])
                pen_points.append(scores[4])
            elif i in m['alliances']['red']['team_keys']:
                scores = get_alliance_cargo_penalty_points(m['key'], 'red')
                telehighscores.append(scores[0])
                telelowscores.append(scores[1])
                autohighscores.append(scores[2])
                autolowscores.append(scores[3])
                pen_points.append(scores[4])
    team_teleop_high_scores[i] = telehighscores
    team_teleop_low_scores[i] = telelowscores
    team_auto_high_scores[i] = autohighscores
    team_auto_low_scores[i] = autolowscores
    team_penalty_points[i] = pen_points

event_averages = [0, 0, 0, 0, 0]
avg_sum = [0, 0, 0, 0, 0]
avg_count = 0

for key in team_teleop_high_scores:
    avg_sum[0] += list_avg(team_teleop_high_scores[key])
    avg_sum[1] += list_avg(team_teleop_low_scores[key])
    avg_sum[2] += list_avg(team_auto_high_scores[key])
    avg_sum[3] += list_avg(team_auto_low_scores[key])
    avg_sum[4] += list_avg(team_penalty_points[key])
    avg_count += 1
for i in range(0, 5):
    event_averages[i] = avg_sum[i] / avg_count

team_teleop_high_score_weight = {}
for key in team_teleop_high_scores:
    average_robot_score = event_averages[0] / 6
    avg = list_avg(team_teleop_high_scores[key]) / 2 - (average_robot_score * 2)
    if avg < 0:
        avg = 0
    team_teleop_high_score_weight[key] = avg

team_teleop_low_score_weight = {}
for key in team_teleop_low_scores:
    average_robot_score = event_averages[1] / 3
    avg = list_avg(team_teleop_low_scores[key]) - (average_robot_score * 2)
    if avg < 0:
        avg = 0
    team_teleop_low_score_weight[key] = avg

team_auto_high_score_weight = {}
for key in team_auto_high_scores:
    average_robot_score = event_averages[2] / 12
    avg = list_avg(team_auto_high_scores[key]) / 4 - (average_robot_score * 2)
    if avg < 0:
        avg = 0
    team_auto_high_score_weight[key] = avg

team_auto_low_score_weight = {}
for key in team_auto_low_scores:
    average_robot_score = event_averages[3] / 6
    avg = list_avg(team_auto_low_scores[key]) / 2 - (average_robot_score * 2)
    if avg < 0:
        avg = 0
    team_auto_low_score_weight[key] = avg

team_penalty_weight = {}
for key in team_penalty_points:
    average_robot_score = event_averages[4] / 12
    avg = list_avg(team_penalty_points[key]) / 4 - (average_robot_score * 2)
    if avg < 0:
        avg = 0
    team_penalty_weight[key] = avg

print('Processing Matches...')

team_total_blame = {}
team_total_cargo_blame = {}
team_total_climb_blame = {}
team_total_penalty_blame = {}

for key in team_teleop_high_scores:
    team_total_blame[key] = [0, 0]
    team_total_cargo_blame[key] = [0, 0]
    team_total_climb_blame[key] = [0, 0]
    team_total_penalty_blame[key] = [0, 0]

for m in matches:
    if '_qm' in m['key']:
        red_blame = [0, 0, 0]
        red_cargo_blame = [0, 0, 0]
        red_climb_blame = [0, 0, 0]
        red_penalty_blame = [0, 0, 0]
        blue_blame = [0, 0, 0]
        blue_cargo_blame = [0, 0, 0]
        blue_climb_blame = [0, 0, 0]
        blue_penalty_blame = [0, 0, 0]
        red_keys = m['alliances']['red']['team_keys']
        blue_keys = m['alliances']['blue']['team_keys']
        red_xtelehighpts = []
        blue_xtelehighpts = []
        red_xtelelowpts = []
        blue_xtelelowpts = []
        red_xautohighpts = []
        blue_xautohighpts = []
        red_xautolowpts = []
        blue_xautolowpts = []
        red_xpenpts = []
        blue_xpenpts = []
        for key in red_keys:
            red_xtelehighpts.append(team_teleop_high_score_weight[key])
            red_xtelelowpts.append(team_teleop_low_score_weight[key])
            red_xautohighpts.append(team_auto_high_score_weight[key])
            red_xautolowpts.append(team_auto_low_score_weight[key])
            red_xpenpts.append(team_penalty_weight[key])
        for key in blue_keys:
            blue_xtelehighpts.append(team_teleop_high_score_weight[key])
            blue_xtelelowpts.append(team_teleop_low_score_weight[key])
            blue_xautohighpts.append(team_auto_high_score_weight[key])
            blue_xautolowpts.append(team_auto_low_score_weight[key])
            blue_xpenpts.append(team_penalty_weight[key])
        red_sums = [sum(red_xtelehighpts),
                    sum(red_xtelelowpts),
                    sum(red_xautohighpts),
                    sum(red_xautolowpts),
                    sum(red_xpenpts)]
        blue_sums = [sum(blue_xtelehighpts),
                     sum(blue_xtelelowpts),
                     sum(blue_xautohighpts),
                     sum(blue_xautolowpts),
                     sum(blue_xpenpts)]
        
        for i in range(0, 5):
            if red_sums[i] == 0:
                red_sums[i] = 1
            if blue_sums[i] == 0:
                blue_sums[i] = 1

        for i in range(0, 3):
            red_xtelehighpts[i] /= red_sums[0]
            red_xtelelowpts[i] /= red_sums[1]
            red_xautohighpts[i] /= red_sums[2]
            red_xautolowpts[i] /= red_sums[3]
            red_xpenpts[i] /= red_sums[4]
            blue_xtelehighpts[i] /= blue_sums[0]
            blue_xtelelowpts[i] /= blue_sums[1]
            blue_xautohighpts[i] /= blue_sums[2]
            blue_xautolowpts[i] /= blue_sums[3]
            blue_xpenpts[i] /= blue_sums[4]
        red_scores = get_alliance_cargo_penalty_points(m['key'], 'red')
        blue_scores = get_alliance_cargo_penalty_points(m['key'], 'blue')
        red_teleop_high_pts = red_scores[0]
        blue_teleop_high_pts = blue_scores[0]
        red_teleop_low_pts = red_scores[1]
        blue_teleop_low_pts = blue_scores[1]
        red_auto_high_pts = red_scores[2]
        blue_auto_high_pts = blue_scores[2]
        red_auto_low_pts = red_scores[3]
        blue_auto_low_pts = blue_scores[3]
        red_pen_pts = red_scores[4]
        blue_pen_pts = blue_scores[4]
        for i in range(0, 3):
            red_climb_pts = did_robot_climb(m['key'], 'red', i + 1)
            blue_climb_pts = did_robot_climb(m['key'], 'blue', i + 1)
            red_cargo_pts = (red_teleop_high_pts * red_xtelehighpts[i] +
                             red_teleop_low_pts * red_xtelelowpts[i] +
                             red_auto_high_pts * red_xautohighpts[i] +
                             red_auto_low_pts * red_xautolowpts[i])
            blue_cargo_pts = (blue_teleop_high_pts * blue_xtelehighpts[i] + 
                              blue_teleop_low_pts * blue_xtelelowpts[i] +
                              blue_auto_high_pts * blue_xautohighpts[i] + 
                              blue_auto_low_pts * blue_xautolowpts[i])
            red_blame[i] += did_robot_taxi(m['key'], 'red', i+1)
            blue_blame[i] += did_robot_taxi(m['key'], 'blue', i+1)
            red_blame[i] += red_climb_pts
            blue_blame[i] += blue_climb_pts
            red_climb_blame[i] += red_climb_pts
            blue_climb_blame[i] += blue_climb_pts
            red_blame[i] += red_cargo_pts
            red_cargo_blame[i] += red_cargo_pts
            blue_blame[i] += blue_cargo_pts
            blue_cargo_blame[i] += blue_cargo_pts
            red_blame[i] -= red_pen_pts * red_xpenpts[i]
            red_penalty_blame[i] += red_pen_pts * red_xpenpts[i]
            blue_blame[i] -= blue_pen_pts * blue_xpenpts[i]
            blue_penalty_blame[i] += blue_pen_pts * blue_xpenpts[i]
        for i in range(0, 3):
            team_total_blame[red_keys[i]][0] += red_blame[i]
            team_total_blame[red_keys[i]][1] += 1
            team_total_cargo_blame[red_keys[i]][0] += red_cargo_blame[i]
            team_total_cargo_blame[red_keys[i]][1] += 1
            team_total_climb_blame[red_keys[i]][0] += red_climb_blame[i]
            team_total_climb_blame[red_keys[i]][1] += 1
            team_total_penalty_blame[red_keys[i]][0] += red_penalty_blame[i]
            team_total_penalty_blame[red_keys[i]][1] += 1
            team_total_blame[blue_keys[i]][0] += blue_blame[i]
            team_total_blame[blue_keys[i]][1] += 1
            team_total_cargo_blame[blue_keys[i]][0] += blue_cargo_blame[i]
            team_total_cargo_blame[blue_keys[i]][1] += 1
            team_total_climb_blame[blue_keys[i]][0] += blue_climb_blame[i]
            team_total_climb_blame[blue_keys[i]][1] += 1
            team_total_penalty_blame[blue_keys[i]][0] += blue_penalty_blame[i]
            team_total_penalty_blame[blue_keys[i]][1] += 1
        if output_match_data == True:
            print('Match ' + m['key'] + ':')
            print(red_keys[0] + ': ' + str(red_blame[0]))
            print(red_keys[1] + ': ' + str(red_blame[1]))
            print(red_keys[2] + ': ' + str(red_blame[2]))
            print(blue_keys[0] + ': ' + str(blue_blame[0]))
            print(blue_keys[1] + ': ' + str(blue_blame[1]))
            print(blue_keys[2] + ': ' + str(blue_blame[2]))

team_blame_per_game = {}
team_cargo_blame_per_game = {}
team_climb_blame_per_game = {}
team_penalty_blame_per_game = {}

for key in teams:
    team_blame_per_game[key] = team_total_blame[key][0] / team_total_blame[key][1]
    team_cargo_blame_per_game[key] = team_total_cargo_blame[key][0] / team_total_cargo_blame[key][1]
    team_climb_blame_per_game[key] = team_total_climb_blame[key][0] / team_total_climb_blame[key][1]
    team_penalty_blame_per_game[key] = team_total_penalty_blame[key][0] / team_total_penalty_blame[key][1]

team_blame_per_game = sort_dic(team_blame_per_game)

table_values = []
columns = [[], [], [], [], [], []]
graph_data = [[], [], [], []]

for key in team_blame_per_game:
    table_values.append([key, team_blame_per_game[key], team_cargo_blame_per_game[key],
                         team_climb_blame_per_game[key], team_penalty_blame_per_game[key]])

for i in range(0, len(table_values)):
    columns[0].append(i + 1)
    columns[1].append(table_values[i][0])
    columns[2].append(table_values[i][1])
    columns[3].append(table_values[i][2])
    columns[4].append(table_values[i][3])
    columns[5].append(table_values[i][4])
    graph_data[0].append(table_values[i][0])
    graph_data[1].append(table_values[i][2])
    graph_data[2].append(table_values[i][3])

print('Done!')

fig = go.Figure(data=[go.Table(header=dict(values=['Rank', 'Team', 'Team Blame per Game', 'Team Cargo Blame per Game',
                                                   'Team Climb Blame per Game', 'Team Penalty Blame per Game']),
                               cells=dict(values=columns))])

fig.show()

plt.scatter(x=graph_data[1], y=graph_data[2])
plt.xlabel('Cargo Blame per Game')
plt.ylabel('Climb Blame per Game')
plt.show()
