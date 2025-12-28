import os

if __name__ == "__main__":
    # Render braucht diesen Port
    port = int(os.environ.get("PORT", 10000))
    # host='0.0.0.0' ist zwingend erforderlich!
    app.run(host='0.0.0.0', port=port)