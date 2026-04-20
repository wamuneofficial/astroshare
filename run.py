from app import create_app

# Создаём экземпляр приложения
app = create_app()

if __name__ == '__main__':
    # debug=True автоматически перезапускает сервер при изменении кода
    # и показывает подробные ошибки в браузере
    app.run(debug=True)
