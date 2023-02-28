import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import ApiGetData
import ta
from ArimaModel import ArimaModel
from io import StringIO
import sys
import plotly.express as px
from PIL import Image

st.set_page_config(page_title='Прогнозирование',page_icon="📶",layout="wide")

st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)

st.markdown('<link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css" integrity="sha384-Gn5384xqQ1aoWXA+058RXPxPg6fy4IWvTNh0E263XmFcJlSAwiGgFAW/dAiS6JXm" crossorigin="anonymous">', unsafe_allow_html=True)

h = st.markdown("""
<style>
div.fullScreenFrame > div {
    display: flex;
    justify-content: center;
}
</style>""", unsafe_allow_html=True)

#Title
original_title = '<p style="text-align: center; color:#3498DB; text-shadow: 2px 2px 4px #000000; font-size: 60px;">Предсказание крипты от меня</p>'
st.markdown(original_title, unsafe_allow_html=True)


st.markdown("Проект Перебаскина Сергея")

st.write('---')
tup, coinname = ApiGetData.getListCoins()


def main():
    #st.sidebar.write("Выберите монету и период")
    #coins = st.sidebar.selectbox("Монета", (tup))
    #period = st.sidebar.selectbox("Выберите период", ("DAY", "1WEEK", "2WEEK", "MONTH"))
    
    # Store the initial value of widgets in session state
    st.header('Выберите монету и период')

    col1, col2 = st.columns(2)

    with col1:
      coins = st.selectbox("Which coin", (tup))

    with col2:
      period = st.selectbox(
        "Choose the period",
        ("DAY", "1WEEK", "2WEEK", "MONTH"))
    
    st.write("View the data and graph")
    col1, col2 = st.columns(2)

    with col1:
       with st.expander("Data"): 
            name = "Coin: " + coinname.get(coins)
            st.subheader(name)
            data = ApiGetData.getFinalData(coins, period)
            st.dataframe(data)

    with col2:
       with st.expander("Graph"): 
            data["MA20"] = ta.trend.sma_indicator(data['close'], window=20)
            data["MA50"] = ta.trend.sma_indicator(data['close'], window=50)
            data["MA100"] = ta.trend.sma_indicator(data['close'], window=100)

            fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        vertical_spacing=0.03,
                        row_width=[0.2, 0.7])

    # Plot OHLC on 1st row
            fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['open'],
                                 high=data['high'],
                                 low=data['low'],
                                 close=data['close'], name="OHLC"),
                  row=1, col=1)
            fig.add_trace(go.Line(x=data.index, y=data['MA20'], name="MA20", line=dict(
            color="purple",
            width=1)))
            fig.add_trace(go.Line(x=data.index, y=data['MA50'], name="MA50", line=dict(
            color="yellow",
            width=1.5)))
            fig.add_trace(go.Line(x=data.index, y=data['MA100'], name="MA100", line=dict(
            color="orange",
            width=2)))

    # Bar trace for volumes on 2nd row without legend
            fig.add_trace(go.Bar(x=data.index, y=data['volume'], showlegend=False), row=2, col=1)

    # Do not show OHLC's rangeslider plot
            fig.update(layout_xaxis_rangeslider_visible=False)

            fig.update_layout(
            autosize=False,
            width=780,
            height=540,
            margin=dict(
            l=50,
            r=50,
            b=50,
            t=50,
            pad=4))

            st.plotly_chart(fig)

    model = ArimaModel(data, period)
    
    st.write('---')
    st.write("Период прогнозирования выберите")
    
    col1, col2 = st.columns(2)

    with col1:
        period = st.slider("Выберите период прогнозирования.", 1, 5, 1)
    with col2:
        st.markdown(' ')

 
    st.write("Нажмите на кнопку .")
    
    if st.button("Начать предсказание"):
      st.warning(model.checkData())
      model.createDataReturn()
      st.write("Stationality test")
      warn, ADF, p_value = model.checkStationarity()
      s1 = "ADF Statistic: " + str(ADF)
      s2 = "p-value: " + str(p_value)
      st.text(s1)
      st.text(s2)
      st.warning(warn)

      st.markdown("**_Процесс займет небольшое количество времени!!!_**")
      with st.expander("Summary SARIMAX Results"):
          result = model.displaySummary()

          old_stdout = sys.stdout
          sys.stdout = mystdout = StringIO()
          print(result.summary())
          sys.stdout = old_stdout
          st.text(mystdout.getvalue())

          pre = model.predict(period)
      
      col1, col2 = st.columns(2)

      with col1:
        st.write("Результаты предсказаний:")
        st.dataframe(pre)

      with col2:
        fig2 = px.line(data, y="close", x=data.index)
        fig2.add_trace(
            go.Scatter(x=pre.index, y=pre['Price_mean'], line=dict(color="red"), name="forecast"))
        fig2.add_trace(go.Scatter(x=pre.index, y=pre['Price_upper'], line=dict(color="green", dash='dash'), name="upper", ))
        fig2.add_trace(go.Scatter(x=pre.index, y=pre['Price_lower'], line=dict(color="green", dash='dash'), name="lower", ))
        st.plotly_chart(fig2)
        
        st.markdown('---')

        
if __name__ == '__main__':
    main()
