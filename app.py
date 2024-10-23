from flask import Flask,jsonify
from gsi import server
import global_data
import time
import threading
app = Flask(__name__)

#checkGlobalData:用于刷新全局变量
def checkGlobalData():
    #current_round用于记录当前回合
    current_round = global_data.data['map']['round']
    check_current_count = current_round
    round_damage = {}
    for i in range(1,11):
        round_damage[i] = allPlayerState()['data'][i]['state']['round_totaldmg']
    while check_current_count == current_round:
        #计算每个选手的adr
        for i in range(1,11):
            adr[i] = (adr[i] + round_damage[i])/2
        # 获取炸弹状态，并使用字典映射更新全局变量
        bomb_state_str = global_data.data['bomb']['state']
        global_data.bomb_state = bomb_state_map.get(bomb_state_str)
        #每次处理完单回合的全局变量后，判断回合是否更新，若更新，则重置所有单回合内的全局变量
        check_current_count = global_data.data['map']['round']     
    global_data.bomb_state = -1

def sendEventMsg():
    #判断炸弹状态是否改变，无改变不打印
    previous_bomb_state = None
    current_bomb_state = global_data.bomb_state
    if previous_bomb_state != current_bomb_state :
        print(global_data.bomb_state_msg[global_data.bomb_state])
        previous_bomb_state = current_bomb_state
    else:
        pass

def backgroundProcess():
    while True:
        checkGlobalData()
        sendEventMsg()
        time.sleep(0.5)

@app.route('/allPlayerState')
def allPlayerState():
    res = {}
    try:
        players = global_data.data['allplayers']
        playerNo = 1
        for player in players:
            res[playerNo] = players[player]
            res[playerNo]['adr'] = adr[playerNo]
            playerNo += 1
        return jsonify({'msg':'请求成功','data':res})
    except Exception as e:
        print(f'发生错误：{e}')
        return jsonify({'msg':'内部异常...','data':{}})
#目前ob的选手数据   
@app.route('/observedPlayer')
def observedPlayer():
    res = {}
    try:
        data = global_data.data['player']
        player_name = data['name']
        allplayers = allPlayerState()['data']
        for player in allplayers:
            if allplayers[player]['name'] == player_name:
                data['adr'] = adr[player]
        res = data
        return jsonify({'msg':'请求成功','data':res})
    except Exception as e:
        print(f'发生错误：{e}')
        return jsonify({'msg':'内部异常...','data':{}})
#选手坐标
@app.route('/positions')
def positions():
    res = {}
    try:
        data = allPlayerState()['data']
        for player in data:
            position = data[player]['position']
            res[player] = position
        return jsonify({'msg':'请求成功','data':res}) 
    except Exception as e:
        print(f'发生错误：{e}')
        return jsonify({'msg':'内部异常...','data':{}})

@app.route('/scores')
def scores():
    ct_wins = 0
    t_wins = 0
    res = {}
    try:
        data = global_data.data['map']
        for round in data['round_wins']:
            if data['round_wins'][round] == 'ct_win_elimination':
                ct_wins += 1
            else:
                t_wins += 1
        res['ct_score'] = ct_wins
        res['t_score'] = t_wins
        return jsonify({'msg':'请求成功','data':res}) 
    except Exception as e:
        print(f'发生错误：{e}')
        return jsonify({'msg':'内部异常...','data':{}})

@app.route('/countdown')
def countdown():
    res = ''
    try:
        res = global_data.data['phase_countdowns']['phase_ends_in']
        return jsonify({'msg':'请求成功','data':res})
    except Exception as e:
        print(f'发生错误：{e}')
        return jsonify({'msg':'内部异常...','data':{}})        

if __name__ == '__main__':
    myServer = server.GSIServer(('127.0.0.1',3000),'S8RL9Z6Y22TYQK45JB4V8PHRJJMD9DS9')
    myServer.start_server()
    #保存炸弹状态对应的状态码
    bomb_state_map = {
        'planting': 0,
        'planted': 1,
        'exploded': 2,
        'defusing': 3,
        'defused': 4,
        'carried': 5,
        'dropped': 6                                                                                        
    }
    #初始化adr
    adr = {}
    for i in range(1,11):
        adr[i] = 0
    thread = threading.Thread(target=backgroundProcess)
    thread.daemon = True
    thread.start()
    app.run(host='0.0.0.0',port=1234,debug=False)

