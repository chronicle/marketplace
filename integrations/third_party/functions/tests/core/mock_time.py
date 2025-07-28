import arrow, datetime


class MockTime:
    @staticmethod
    def convert_time_format(request):
        """Преобразует время в заданный формат."""
        time_input = request.get("time_input", "").strip()  # Убираем лишние пробелы
        from_format = request.get("from_format")
        to_format = request.get("to_format")
        time_delta = request.get("time_delta_in_seconds", 0)
        timezone = request.get("timezone")

        if not time_input or not from_format or not to_format:
            raise ValueError("Missing time input or format parameters")

        # 1. Парсинг входной даты/времени с учетом типа формата
        try:
            if '%' in from_format:
                # Формат в стиле datetime.strptime
                try:
                    # Используем Arrow.strptime для форматов с %
                    new_time = arrow.Arrow.strptime(time_input, from_format)
                except Exception:
                    # Резервный вариант: стандартный datetime.strptime
                    dt_obj = datetime.datetime.strptime(time_input, from_format)
                    new_time = arrow.get(dt_obj)  # преобразовать datetime в Arrow
            else:
                # Формат в стиле Arrow (YYYY, MM, DD и т.д.)
                new_time = arrow.get(time_input, from_format)
        except Exception as e:
            # Если ни один способ не сработал, сообщаем об ошибке
            raise ValueError(f"Failed to parse time with format {from_format}: {e}")

        # 2. Применяем сдвиг времени и изменение часового пояса, если указаны
        if time_delta:
            new_time = new_time.shift(seconds=time_delta)
        if timezone:
            new_time = new_time.to(timezone)

        # 3. Форматируем выходную строку в нужный формат
        if '%' in to_format:
            # Используем встроенный datetime и strftime для форматов с %
            result_time_str = new_time.datetime.strftime(to_format)
        else:
            # Формат в стиле Arrow
            result_time_str = new_time.format(to_format)

        return {"time": result_time_str}
