# Observability

## Local Development

The app is built to support bog-typical Flask local development.

```shell
export FLASK_DEBUG=true
export OBSERVABILITY_CONFIG=development
flask run -p 5000
```

You can also use the PyCharm built-in Flask Run Configuration.  The settings to change:
- **Target Type:**  Module name
- **Target:**  `app`
- **Application:**  `app`
- **Additional Options:**  `-p 5000`
- **OBSERVABILITY_CONFIG:**  `development`
- **FLASK_DEBUG:**  :white_check_mark:
- **Working Directory:**  Your work tree root

Once you set that run configuration up, you can just click the "Debug" button for the config and it will run the app in debug mode.
This supports breakpoints, and the app will also hot-reload on detected file changes!  The app will be running at `http://localhost:5000/...`.

