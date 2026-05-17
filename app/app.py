from flask import Flask, render_template
from models import ItemModel

app = Flask(__name__)
model = ItemModel()

@app.route('/')
def index():
    # Контроллер запрашивает данные у модели
    items = model.get_all_items()
    # И передает их в представление (шаблон)
    return render_template('index.html', items=items)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
