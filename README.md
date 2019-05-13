# Singer AppFigures Tap

This is a [Singer](https://singer.io) tap that produces JSON-formatted data
following the [Singer
spec](https://github.com/singer-io/getting-started/).

This tap:

- Pulls raw data from the [AppFigures API](https://docs.appfigures.com/)
- Extracts the following resources:
  - [Products](https://docs.appfigures.com/products)
  - [Sales Reports](https://docs.appfigures.com/api/reference/v2/sales)
  - [Revenue Reports](https://docs.appfigures.com/api/reference/v2/revenue)
  - [Ratings Reports](https://docs.appfigures.com/api/reference/v2/reports-ratings)
  - [Usage Reports](https://docs.appfigures.com/api/reference/v2/usage)
  - [Ranks](https://docs.appfigures.com/api/reference/v2/ranks)
- Outputs the schema for each resource
- Incrementally pulls data based on the end state of the previous run


## Getting Started

For more examples and information about running a singer tap see the [singer instructions](https://github.com/singer-io/getting-started/blob/master/docs/RUNNING_AND_DEVELOPING.md). 

### Installation and configuration
Create a config.json with the following content:
```
{
  "username": "....",
  "password": "...",
  "api_key": "...",
  "start_date": "2019-04-15"
}
```

The tap will retrieve all data starting from the start_date. Format: YYYY-MM-DD

Then:
```
python3 -m venv ~/.virtualenvs/tap-appfigures
source ~/.virtualenvs/tap-appfigures/bin/activate
pip install git+https://github.com/MeowWolf/tap-appfigures
```

### Running the tap
```~/.virtualenvs/tap-appfigures/bin/tap-appfigures --config config.json --state state.json```

The --state is a required parameter. 

Do not create the file (typically) state.json yourself. The script will create it on the first run, to record the end state of the import process.

## Authors

* Developed for [**Meow Wolf**](https://meowwolf.com/)
* **Coen de Groot** - *Initial work* - [Compass Mentis](http://www.compassmentis.com/),

## License

This project is licensed under the GNU AFFERO GENERAL PUBLIC License - see the [LICENSE.md](LICENSE.md) file for details
MIT