import traceback
try:
    import langchain_google_genai.chat_models
    print("Imported successfully!")
except Exception as e:
    with open("import_error2.txt", "w") as f:
        f.write(traceback.format_exc())
    print("Wrote error to import_error2.txt")
