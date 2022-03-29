import requests
import json

import plotly.graph_objects as go

#######################################################################################
# DON'T EDIT ANYTHING OTHER THAN THESE VARIABLES IF YOU DON'T KNOW WHAT YOU ARE DOING
api_key = ''
event_key = '2022mndu2'
#######################################################################################

if api_key == '':
    print('No API key entered!')
    exit(2549)
if event_key == '':
    print('No event key entered!')
    exit(2550)

headers = {'X-TBA-Auth-Key': api_key}

url = 'https://www.thebluealliance.com/api/v3/match/2022iacf_f1m3'
match = json.loads(requests.get(url, headers=headers).text)


# key = TBA match key (e.g. '2022iacf_qm22') --- alliance = 'red' or 'blue'
def get_alliance_score(key, alliance):
    url = 'https://www.thebluealliance.com/api/v3/match/' + key
    match = json.loads(requests.get(url, headers=headers).text)
    return match['alliances'][alliance]['score']


# gets score that an alliance scored thru shooting, excluding taxi, penalty, and endgame points
def get_alliance_match_auto_low_cargo_score(key, alliance):
    url = 'https://www.thebluealliance.com/api/v3/match/' + key
    match = json.loads(requests.get(url, headers=headers).text)
    # print(match)
    return (match['score_breakdown'][alliance]['autoCargoLowerBlue'] +
            match['score_breakdown'][alliance]['autoCargoLowerRed'] +
            match['score_breakdown'][alliance]['autoCargoLowerNear'] +
            match['score_breakdown'][alliance]['autoCargoLowerFar']) * 2


def get_alliance_match_auto_high_cargo_score(key, alliance):
    url = 'https://www.thebluealliance.com/api/v3/match/' + key
    match = json.loads(requests.get(url, headers=headers).text)
    # print(match)
    return (match['score_breakdown'][alliance]['autoCargoUpperBlue'] +
            match['score_breakdown'][alliance]['autoCargoUpperRed'] +
            match['score_breakdown'][alliance]['autoCargoUpperNear'] +
            match['score_breakdown'][alliance]['autoCargoUpperFar']) * 4


def get_alliance_match_teleop_low_cargo_score(key, alliance):
    url = 'https://www.thebluealliance.com/api/v3/match/' + key
    match = json.loads(requests.get(url, headers=headers).text)
    # print(match)
    return (match['score_breakdown'][alliance]['teleopCargoLowerBlue'] +
            match['score_breakdown'][alliance]['teleopCargoLowerRed'] +
            match['score_breakdown'][alliance]['teleopCargoLowerNear'] +
            match['score_breakdown'][alliance]['teleopCargoLowerFar'])


def get_alliance_match_teleop_high_cargo_score(key, alliance):
    url = 'https://www.thebluealliance.com/api/v3/match/' + key
    match = json.loads(requests.get(url, headers=headers).text)
    # print(match)
    return (match['score_breakdown'][alliance]['teleopCargoUpperBlue'] +
            match['score_breakdown'][alliance]['teleopCargoUpperRed'] +
            match['score_breakdown'][alliance]['teleopCargoUpperNear'] +
            match['score_breakdown'][alliance]['teleopCargoUpperFar']) * 2


def get_alliance_penalty_points(key, opposing_alliance):
    url = 'https://www.thebluealliance.com/api/v3/match/' + key
    match = json.loads(requests.get(url, headers=headers).text)
    return match['score_breakdown'][opposing_alliance]['foulPoints']


def did_robot_taxi(key, alliance, position):
    url = 'https://www.thebluealliance.com/api/v3/match/' + key
    match = json.loads(requests.get(url, headers=headers).text)
    if match['score_breakdown'][alliance]['taxiRobot' + str(position)] == 'Yes':
        return 2
    elif match['score_breakdown'][alliance]['taxiRobot' + str(position)] == 'No':
        return 0
    else:
        print('taxi fucky wucky')


def did_robot_climb(key, alliance, position):
    url = 'https://www.thebluealliance.com/api/v3/match/' + key
    match = json.loads(requests.get(url, headers=headers).text)
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
        print('climb fucky wucky')
        return 600000000004


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

for i in teams:
    print('Now processing ' + i + ' (' + str(teams.index(i) + 1) + '/' + str(len(teams)) + ')')
    telehighscores = []
    telelowscores = []
    autohighscores = []
    autolowscores = []
    pen_points = []
    for m in matches:
        if '_qm' in m['key']:
            if i in m['alliances']['blue']['team_keys']:
                telehighscores.append(get_alliance_match_teleop_high_cargo_score(m['key'], 'blue'))
                telelowscores.append(get_alliance_match_teleop_low_cargo_score(m['key'], 'blue'))
                autohighscores.append(get_alliance_match_auto_high_cargo_score(m['key'], 'blue'))
                autolowscores.append(get_alliance_match_auto_low_cargo_score(m['key'], 'blue'))
                pen_points.append(get_alliance_penalty_points(m['key'], 'red'))
                # print(i + ', ' + m['key'] + ': ' + str(get_alliance_match_cargo_score(m['key'], 'blue')))
            elif i in m['alliances']['red']['team_keys']:
                telehighscores.append(get_alliance_match_teleop_high_cargo_score(m['key'], 'red'))
                telelowscores.append(get_alliance_match_teleop_low_cargo_score(m['key'], 'red'))
                autohighscores.append(get_alliance_match_auto_high_cargo_score(m['key'], 'red'))
                autolowscores.append(get_alliance_match_auto_low_cargo_score(m['key'], 'red'))
                pen_points.append(get_alliance_penalty_points(m['key'], 'blue'))
                # print(i + ', ' + m['key'] + ': ' + str(get_alliance_match_cargo_score(m['key'], 'red')))
    team_teleop_high_scores[i] = telehighscores
    team_teleop_low_scores[i] = telelowscores
    team_auto_high_scores[i] = autohighscores
    team_auto_low_scores[i] = autolowscores
    team_penalty_points[i] = pen_points

team_teleop_high_score_averages = {}
for key in team_teleop_high_scores:
    pts_sum = 0
    count = 0
    for i in team_teleop_high_scores[key]:
        pts_sum += i
        count += 1
    avg = pts_sum / count
    team_teleop_high_score_averages[key] = avg

team_teleop_low_score_averages = {}
for key in team_teleop_low_scores:
    pts_sum = 0
    count = 0
    for i in team_teleop_low_scores[key]:
        pts_sum += i
        count += 1
    avg = pts_sum / count
    team_teleop_low_score_averages[key] = avg

team_auto_high_score_averages = {}
for key in team_auto_high_scores:
    pts_sum = 0
    count = 0
    for i in team_auto_high_scores[key]:
        pts_sum += i
        count += 1
    avg = pts_sum / count
    team_auto_high_score_averages[key] = avg

team_auto_low_score_averages = {}
for key in team_auto_low_scores:
    pts_sum = 0
    count = 0
    for i in team_auto_low_scores[key]:
        pts_sum += i
        count += 1
    avg = pts_sum / count
    team_auto_low_score_averages[key] = avg

team_penalty_averages = {}
for key in team_penalty_points:
    pts_sum = 0
    count = 0
    for i in team_penalty_points[key]:
        pts_sum += i
        count += 1
    avg = pts_sum / count
    team_penalty_averages[key] = avg

print('done!')

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
            red_xtelehighpts.append(team_teleop_high_score_averages[key])
            red_xtelelowpts.append(team_teleop_low_score_averages[key])
            red_xautohighpts.append(team_auto_high_score_averages[key])
            red_xautolowpts.append(team_auto_low_score_averages[key])
            red_xpenpts.append(team_penalty_averages[key])
        for key in blue_keys:
            blue_xtelehighpts.append(team_teleop_high_score_averages[key])
            blue_xtelelowpts.append(team_teleop_low_score_averages[key])
            blue_xautohighpts.append(team_auto_high_score_averages[key])
            blue_xautolowpts.append(team_auto_low_score_averages[key])
            blue_xpenpts.append(team_penalty_averages[key])
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
        # red_pts = get_alliance_score(m[key], 'red')
        # blue_pts = get_alliance_score(m[key], 'blue')
        red_teleop_high_pts = get_alliance_match_teleop_high_cargo_score(m['key'], 'red')
        blue_teleop_high_pts = get_alliance_match_teleop_high_cargo_score(m['key'], 'blue')
        red_teleop_low_pts = get_alliance_match_teleop_low_cargo_score(m['key'], 'red')
        blue_teleop_low_pts = get_alliance_match_teleop_low_cargo_score(m['key'], 'blue')
        red_auto_high_pts = get_alliance_match_auto_high_cargo_score(m['key'], 'red')
        blue_auto_high_pts = get_alliance_match_auto_high_cargo_score(m['key'], 'blue')
        red_auto_low_pts = get_alliance_match_auto_low_cargo_score(m['key'], 'red')
        blue_auto_low_pts = get_alliance_match_auto_low_cargo_score(m['key'], 'blue')
        red_pen_pts = get_alliance_penalty_points(m['key'], 'blue')
        blue_pen_pts = get_alliance_penalty_points(m['key'], 'red')
        for i in range(0, 3):
            red_climb_pts = did_robot_climb(m['key'], 'red', i+1)
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

for key in team_blame_per_game:
    print(key)
    table_values.append([key, team_blame_per_game[key], team_cargo_blame_per_game[key],
                         team_climb_blame_per_game[key], team_penalty_blame_per_game[key]])

for i in range(0, len(table_values)):
    columns[0].append(i + 1)
    columns[1].append(table_values[i][0])
    columns[2].append(table_values[i][1])
    columns[3].append(table_values[i][2])
    columns[4].append(table_values[i][3])
    columns[5].append(table_values[i][4])

fig = go.Figure(data=[go.Table(header=dict(values=['Rank', 'Team', 'Team Blame per Game', 'Team Cargo Blame per Game',
                                                   'Team Climb Blame per Game', 'Team Penalty Blame per Game']),
                               cells=dict(values=columns))])

fig.show()
