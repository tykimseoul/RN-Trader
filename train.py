from agent import Agent
from functions import *
import sys
import matplotlib.pyplot as plt
import time
from functools import reduce

if len(sys.argv) != 4:
    print("Usage: python train.py [stock] [window] [episodes]")
    exit()
np.set_printoptions(linewidth=np.inf)
stock_name, window_size, episode_count = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])

agent = Agent(window_size)
data = get_stock_data(stock_name, '2019/12/16', '2019/12/21')
train_data_size = len(data) - 1
batch_size = 64
profits = []

for e in range(episode_count + 1):
    print("Episode " + str(e) + "/" + str(episode_count))

    total_profit = 0
    agent.inventory = []
    start = time.time()
    state = get_state(data, 0, window_size + 1, len(agent.inventory))

    for t in range(train_data_size):
        action, count = agent.act(state)
        # print('choice', action, count)

        # sit
        reward = 0
        # buy
        if action == 1 and count > 0:
            for _ in range(count):
                agent.inventory.append(data[t])
            print('Ep {ep}/{ep_count}:{m}\tBuy {cnt}:\t{price}'.format(ep=e, ep_count=episode_count, m=t, cnt=count, price=format_price(data[t] * count)))
        # sell
        elif action == 2 and count > 0 and len(agent.inventory) > 0:
            sellable_count = min(count, len(agent.inventory))
            purchase_sum = reduce((lambda x, y: x + y), [agent.inventory.pop() for p in range(sellable_count)])
            profit = data[t] * sellable_count - purchase_sum
            reward = max(profit, 0)
            total_profit += profit
            count = sellable_count
            print('Ep {ep}/{ep_count}:{m}\tSell {cnt}:\t{price} | Profit:\t{profit}'.format(ep=e, ep_count=episode_count, m=t, cnt=sellable_count, price=format_price(data[t] * sellable_count),
                                                                                            profit=format_price(profit)))

        next_state = get_state(data, t + 1, window_size + 1, len(agent.inventory))

        done = t == train_data_size - 1
        agent.memory.append((state, action, count, reward, next_state, done))
        state = next_state

        if done:
            end = time.time()
            print("--------------------------------")
            print("Total Profit: " + format_price(total_profit))
            print("Time Elapsed: " + format_time(end - start))
            print("--------------------------------")
            profits.append(total_profit)

        if len(agent.memory) > batch_size:
            agent.update_model(batch_size)

    if e % 100 == 0:
        agent.model.save('model/model_ep' + str(e))

plt.plot(profits)
plt.show()
