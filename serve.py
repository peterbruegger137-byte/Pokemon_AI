import os

if __name__ == "__main__":
    # Render weist dir diesen Port zu
    port = int(os.environ.get("PORT", 10000))
    # '0.0.0.0' ist nötig, damit die Cloud-Anfragen durchkommen
    app.run(host='0.0.0.0', port=port)