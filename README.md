# Covid-19ITA

#### :warning: This project was developed for educational purposes without any support: do not use it as a data source or as an official channel from authority :warning:

Covid-19ITA is a Telegram bot (**ItaCovidBot**) which responds with some small data from Covid-19 epidemic in Italy.

Source of numbers is the official [COVID-19](https://github.com/pcm-dpc/COVID-19), updated every day at 18:30 CET when data are usually published; all project is hosted on AWS, with a lambda function and a CloudWatch trigger for the automatic update process.

##### Available commands:
- **/oggi**
- **/totale**
- **/provincia *[name]***
