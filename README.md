## What

A toolbar app for mac that show the current status of the electricity (is On or Cutoff) in Lebanon.

More background informations in [this blog post](https://mhasbini.com/blog/introducing-electricity-cutoff-app.html).

## ScreenShots

![Screenshot 1](screenshots/2.png)
![Screenshot 2](screenshots/1.png)

## Development

- Install requirements: `pip3 install -r requirements.txt`.
- Package:
  - `fbs freeze`
  - `fbs installer`
- Run tests: `python3 -m unittest discover -s src/main/python/ -p 'test_*.py'`
- Run linter: `black src/main/python/`