# Базовый класс всех шаблонов
class Template:
    # Возвращает поля шаблона
    def get_fields(self):
        pass

    # Должно возвращать адрес файла-результата
    def fill(self, fields) -> str:
        pass
