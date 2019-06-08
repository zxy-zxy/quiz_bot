# Python quiz-bot

This is a bot application which is designed to conduct a quizes on 
[Vk](https://vk.com) and [Telegram](https://telegram.org/) platforms.

Questions are provided at *data/quiz-questions* directory. 

Feel free to populate quiz with your own questions! 

All you need is to 
follow with the file format that is necessary for the correct operation of the parser.

### Usage

#### Telegram configuration
1. Obtain a token for your bot from [botfather](https://core.telegram.org/bots).

#### Vk configuration
1. Create a group at [https://vk.com](Vk).
2. Obtain a group token.

### Development with docker-compose

Build with docker-compose:
```bash
docker-compose -f docker-compose-dev.yml build
```
Run:
```bash
docker-compose -f docker-compose-dev.yml up
```

### Deployment with Heroku
This application requires Heroku-redis add-on.
* To deploy this app on Heroku you need to setup environment variable APPLICATION_ENV=production.
* Activate Heroku-redis add-on on your account.

* Login with [Heroku cli](https://devcenter.heroku.com/articles/heroku-cli):
    ```bash
    heroku login
    ```
* To reveal configuration variables:
    ```bash
    heroku config --app <your_application_name_here>
    ```
* Run application and track logs:
    ```bash
    heroku ps:scale populate-db=1 --app <your_application_name_here>
    heroku ps:scale bot-telegram=1 --app <your_application_name_here>
    heroku ps:scale bot-vk=1 --app <your_application_name_here>
    heroku logs --tail --app <your_application_name_here>
    ```