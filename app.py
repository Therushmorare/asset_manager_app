from my_factory import create_app

# Create the Flask app instance
app = create_app()

# Optional: only for local development
if __name__ == "__main__":
    app.run(debug=True)