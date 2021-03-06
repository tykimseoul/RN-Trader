from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense
from keras.optimizers import Adam

import numpy as np
import random
from collections import deque


class Agent:
    def __init__(self, state_size, is_eval=False, model_name=""):
        self.state_size = state_size  # normalized previous days
        self.action_size = 3  # sit, buy, sell
        self.memory = deque(maxlen=1000)
        self.inventory = []
        self.model_name = model_name
        self.is_eval = is_eval

        self.discount = 0.95
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.997

        self.max_stock_trade = 6

        self.model = load_model("model/" + model_name) if is_eval else self._model()

    def _model(self):
        model = Sequential()
        model.add(Dense(units=128, input_dim=self.state_size + 1, activation="relu"))
        model.add(Dense(units=64, activation="relu"))
        model.add(Dense(units=32, activation="relu"))
        model.add(Dense(units=32, activation="relu"))
        model.add(Dense(1 + (self.action_size - 1) * self.max_stock_trade, activation="linear"))
        model.compile(loss="mse", optimizer=Adam(lr=0.001))

        return model

    def act(self, state):
        if not self.is_eval and random.random() <= self.epsilon:
            action = random.randrange(self.action_size)
            if action == 0:
                return action, 0
            else:
                return action, random.randrange(1, self.max_stock_trade + 1)

        actions = self.model.predict(state)[0]
        if np.isnan(actions).any():
            print("warning: nan actions ===============")
        idx = np.argmax(actions)
        if idx == 0:
            return 0, 0
        else:
            action = (idx - 1) // self.max_stock_trade
            count = (idx - 1) % self.max_stock_trade
            return action, count

    def update_model(self, batch_size):
        memory_size = len(self.memory)
        mini_batch = [self.memory[i] for i in range(memory_size - batch_size + 1, memory_size)]

        for state, action, count, reward, next_state, done in mini_batch:
            target = reward
            if not done:
                target = reward + self.discount * np.amax(self.model.predict(next_state)[0])

            target *= 0.01
            target_f = self.model.predict(state)
            target_f[0][max(0, (action - 1) * self.max_stock_trade + count)] = target
            self.model.fit(state, target_f, epochs=1, verbose=0)

        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
