import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from math import floor

plt.rcParams["figure.figsize"] = (20, 10)
plt.style.use("fivethirtyeight")


def get_macd(price, slow, fast, smooth):
    exp1 = price.ewm(span=fast, adjust=False).mean()
    exp2 = price.ewm(span=slow, adjust=False).mean()
    macd = pd.DataFrame(exp1 - exp2).rename(columns={"close": "macd"})
    signal = pd.DataFrame(macd.ewm(span=smooth, adjust=False).mean()).rename(
        columns={"macd": "signal"}
    )
    hist = pd.DataFrame(macd["macd"] - signal["signal"]).rename(columns={0: "hist"})
    df = pd.concat([macd, signal, hist], axis=1)
    return df


def implement_macd_strategy(prices, data):
    buy_price = []
    sell_price = []
    macd_signal = []
    signal = 0

    for i in range(len(data)):
        if data["macd"][i] > data["signal"][i]:
            if signal != 1:
                buy_price.append(prices[i])
                sell_price.append(np.nan)
                signal = 1
                macd_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                macd_signal.append(0)
        elif data["macd"][i] < data["signal"][i]:
            if signal != -1:
                buy_price.append(np.nan)
                sell_price.append(prices[i])
                signal = -1
                macd_signal.append(signal)
            else:
                buy_price.append(np.nan)
                sell_price.append(np.nan)
                macd_signal.append(0)
        else:
            buy_price.append(np.nan)
            sell_price.append(np.nan)
            macd_signal.append(0)

    return buy_price, sell_price, macd_signal


def plot_signals_macd(df_price, macd_df, buy_price, sell_price, label):
    ax1 = plt.subplot2grid((8, 1), (0, 0), rowspan=4, colspan=1)
    ax2 = plt.subplot2grid((8, 1), (5, 0), rowspan=3, colspan=1)

    ax1.plot(df_price["close"], color="skyblue", linewidth=2, label=label)
    ax1.plot(
        df_price.index,
        buy_price,
        marker="^",
        color="green",
        markersize=10,
        label="BUY SIGNAL",
        linewidth=0,
    )
    ax1.plot(
        df_price.index,
        sell_price,
        marker="v",
        color="r",
        markersize=10,
        label="SELL SIGNAL",
        linewidth=0,
    )
    ax1.legend()
    ax1.set_title(f"{label} MACD SIGNALS")
    ax2.plot(macd_df["macd"], color="grey", linewidth=1.5, label="MACD")
    ax2.plot(macd_df["signal"], color="skyblue", linewidth=1.5, label="SIGNAL")

    for i in range(len(macd_df)):
        if str(macd_df["hist"][i])[0] == "-":
            ax2.bar(macd_df.index[i], macd_df["hist"][i], color="#ef5350")
        else:
            ax2.bar(macd_df.index[i], macd_df["hist"][i], color="#26a69a")

    plt.legend(loc="lower right")
    plt.show()

    
def get_best_params_macd(df_price, slow, fast, smooth, investment_value):
    df_macd = get_macd(df_price['close'], slow, fast, smooth)
    buy_price, sell_price, macd_signal = implement_macd_strategy(df_price['close'], df_macd)
    
    position = []
    for i in range(len(macd_signal)):
        if macd_signal[i] > 1:
            position.append(0)
        else:
            position.append(1)

    for i in range(len(df_price['close'])):
        if macd_signal[i] == 1:
            position[i] = 1
        elif macd_signal[i] == -1:
            position[i] = 0
        else:
            position[i] = position[i-1]

    macd = df_macd['macd']
    signal = df_macd['signal']
    close_price = df_price['close']

    macd_signal = pd.DataFrame(macd_signal).rename(columns={0:'macd_signal'}).set_index(df_price.index)
    position = pd.DataFrame(position).rename(columns={0:'macd_position'}).set_index(df_price.index)

    strategy = pd.concat([close_price, macd, signal, macd_signal, position], axis=1)

    df_ret = pd.DataFrame(np.diff(df_price['close'])).rename(columns = {0:'returns'})
    macd_strategy_ret = []

    for i in range(len(df_ret)):
        try:
            returns = df_ret['returns'][i] * strategy['macd_position'][i]
            macd_strategy_ret.append(returns)
        except:
            pass

    macd_strategy_ret_df = pd.DataFrame(macd_strategy_ret).rename(columns = {0:'macd_returns'})
    
    number_of_stocks = floor(investment_value / df_price['close'][0])
    macd_investment_ret = []

    for i in range(len(macd_strategy_ret_df['macd_returns'])):
        returns = number_of_stocks * macd_strategy_ret_df['macd_returns'][i]
        macd_investment_ret.append(returns)

    macd_investment_ret_df = pd.DataFrame(macd_investment_ret).rename(columns={0:'investment_returns'})
    total_investment_ret = round(sum(macd_investment_ret_df['investment_returns']), 2)
    profit_percentage = floor((total_investment_ret / investment_value)*100)
    
    return total_investment_ret, profit_percentage
