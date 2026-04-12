from app.main import create_app

app = create_app()

if __name__ == "__main__":
    # Intentionally left as a dev-friendly entrypoint (do not use for production).
    # Note: disabling the reloader keeps the process stable when launched from VS Code tasks/background terminals.
    app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
